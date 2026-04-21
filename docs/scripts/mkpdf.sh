#!/usr/bin/env bash
set -euo pipefail

# This wrapper keeps the runtime contract deliberately small. The Python
# assembler writes unified Markdown files and emits only the per-render paths
# that vary between guides, while this shell script owns the Pandoc container
# defaults and any invocation-time overrides.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DOCS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd -- "${DOCS_ROOT}/.." && pwd)"
ASSEMBLER="${SCRIPT_DIR}/assemble-markdown.py"
PYTHON="${PYTHON:-python3}"

CONFIG_PATH="${PDF_CONFIG:-pdf.toml}"
PANDOC_IMAGE_OVERRIDE="${PDF_PANDOC_IMAGE:-}"
PANDOC_DEFAULTS_OVERRIDE="${PDF_PANDOC_DEFAULTS:-}"
PANDOC_MOUNT_ROOT_OVERRIDE="${PDF_PANDOC_MOUNT_ROOT:-}"
CACHE_HOME_OVERRIDE="${PDF_CACHE_HOME:-}"
CACHE_XDG_CACHE_OVERRIDE="${PDF_CACHE_XDG_CACHE:-}"
ASSEMBLER_ARGS=()
CLEAN_REQUESTED=0
GUIDE_TARGETS=()

resolve_docs_path() {
    local raw_path="$1"
    if [[ "$raw_path" = /* ]]; then
        printf '%s\n' "$raw_path"
    else
        printf '%s/%s\n' "$DOCS_ROOT" "$raw_path"
    fi
}

build_container_texinputs() {
    local defaults_path="$1"
    local docs_root="$2"
    local mount_root="${3%/}"
    if [[ -z "$mount_root" ]]; then
        mount_root="/docs"
    fi

    "$PYTHON" - "$defaults_path" "$docs_root" "$mount_root" <<'PY'
from pathlib import Path
import sys

defaults_path = Path(sys.argv[1]).resolve()
docs_root = Path(sys.argv[2]).resolve()
mount_root = sys.argv[3].rstrip("/") or "/docs"

# Keep TEXINPUTS aligned with Pandoc's resource-path entries so the LaTeX phase
# searches the same directories, in the same order, as the Pandoc phase. We
# intentionally parse only the simple list form used in this repo's defaults
# file instead of adding a YAML dependency to the wrapper.
paths: list[str] = []
in_resource_path = False
for raw_line in defaults_path.read_text(encoding="utf-8").splitlines():
    line = raw_line.rstrip()
    stripped = line.strip()

    if not in_resource_path:
        if stripped == "resource-path:":
            in_resource_path = True
        continue

    if not stripped:
        continue

    if raw_line.startswith("  - "):
        resource_value = raw_line.split("- ", 1)[1].strip()
        resource_path = Path(resource_value)
        if resource_path.is_absolute():
            if resource_path.is_relative_to(docs_root):
                relative = resource_path.relative_to(docs_root)
                paths.append(f"{mount_root}/{relative.as_posix()}")
            else:
                paths.append(resource_path.as_posix())
        else:
            paths.append(resource_path.as_posix())
        continue

    if not raw_line.startswith("  "):
        break

print(":".join(paths) + ":")
PY
}

container_path() {
    "$PYTHON" - "$DOCS_ROOT" "$PANDOC_MOUNT_ROOT" "$1" <<'PY'
from pathlib import Path
import sys

docs_root = Path(sys.argv[1]).resolve()
mount_root = sys.argv[2].rstrip("/") or "/docs"
path = Path(sys.argv[3]).resolve()
try:
    relative = path.relative_to(docs_root)
except ValueError as exc:
    raise SystemExit(f"path is outside docs root and cannot be mounted: {path}") from exc
print(f"{mount_root}/{relative.as_posix()}")
PY
}

while (($#)); do
    case "$1" in
        --clean)
            CLEAN_REQUESTED=1
            ASSEMBLER_ARGS+=("clean")
            shift
            ;;
        --config)
            CONFIG_PATH="$2"
            ASSEMBLER_ARGS+=("$1" "$2")
            shift 2
            ;;
        --pandoc-image)
            PANDOC_IMAGE_OVERRIDE="$2"
            ASSEMBLER_ARGS+=("$1" "$2")
            shift 2
            ;;
        --pandoc-defaults)
            PANDOC_DEFAULTS_OVERRIDE="$2"
            ASSEMBLER_ARGS+=("$1" "$2")
            shift 2
            ;;
        --pandoc-mount-root)
            PANDOC_MOUNT_ROOT_OVERRIDE="$2"
            ASSEMBLER_ARGS+=("$1" "$2")
            shift 2
            ;;
        --cache-home)
            CACHE_HOME_OVERRIDE="$2"
            shift 2
            ;;
        --cache-xdg-cache)
            CACHE_XDG_CACHE_OVERRIDE="$2"
            shift 2
            ;;
        *)
            if [[ "$1" == --* ]]; then
                ASSEMBLER_ARGS+=("$1")
            else
                GUIDE_TARGETS+=("$1")
            fi
            shift
            ;;
    esac
done

if ((CLEAN_REQUESTED)); then
    exec "$PYTHON" "$ASSEMBLER" "${ASSEMBLER_ARGS[@]}"
fi

mapfile -t CONFIG_VALUES < <(
    "$PYTHON" - "$DOCS_ROOT" "$CONFIG_PATH" <<'PY'
from pathlib import Path
import sys
import tomllib

docs_root = Path(sys.argv[1]).resolve()
config_arg = Path(sys.argv[2])
config_path = config_arg if config_arg.is_absolute() else docs_root / config_arg
with config_path.open("rb") as handle:
    data = tomllib.load(handle)

def resolve_docs_path(raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else docs_root / path

output_dir = resolve_docs_path(data.get("output_dir", "pdf"))
print(resolve_docs_path(data.get("pandoc_defaults", "pandoc/defaults.yaml")))
print(data.get("pandoc_image", "genestack-docs-pandoc:latest"))
print(data.get("pandoc_mount_root", "/docs"))
print(output_dir / "temp" / "home")
print(output_dir / "temp" / "xdg-cache")
PY
)

load_all_guides() {
    "$PYTHON" - "$DOCS_ROOT" "$CONFIG_PATH" <<'PY'
from pathlib import Path
import sys
import tomllib

docs_root = Path(sys.argv[1]).resolve()
config_arg = Path(sys.argv[2])
config_path = config_arg if config_arg.is_absolute() else docs_root / config_arg
with config_path.open("rb") as handle:
    data = tomllib.load(handle)

for guide in data.get("guides", []):
    slug = guide.get("slug", "").strip()
    if slug:
        print(slug)
PY
}

PANDOC_DEFAULTS="$(resolve_docs_path "${PANDOC_DEFAULTS_OVERRIDE:-${CONFIG_VALUES[0]}}")"
PANDOC_IMAGE="${PANDOC_IMAGE_OVERRIDE:-${CONFIG_VALUES[1]}}"
PANDOC_MOUNT_ROOT="${PANDOC_MOUNT_ROOT_OVERRIDE:-${CONFIG_VALUES[2]}}"
CACHE_HOME_HOST="$(resolve_docs_path "${CACHE_HOME_OVERRIDE:-${CONFIG_VALUES[3]}}")"
CACHE_XDG_CACHE_HOST="$(resolve_docs_path "${CACHE_XDG_CACHE_OVERRIDE:-${CONFIG_VALUES[4]}}")"

if ! docker image inspect "$PANDOC_IMAGE" >/dev/null 2>&1; then
    printf '[pdf] missing image: %s\n' "$PANDOC_IMAGE" >&2
    printf '[pdf] run `make -C %s deps` before invoking the PDF builder\n' "$DOCS_ROOT" >&2
    exit 1
fi

run_assembler() {
    "$PYTHON" "$ASSEMBLER" "${ASSEMBLER_ARGS[@]}" "$@"
}

render_pending_renders() {
    local render_line input_path output_path state_path state_payload
    local input_label output_label
    local pending_renders=("$@")

    if ((${#pending_renders[@]} == 0)); then
        return 0
    fi

    for render_line in "${pending_renders[@]}"; do
        IFS=$'\t' read -r input_path output_path state_path state_payload <<< "$render_line"
        mkdir -p "$CACHE_HOME_HOST" "$CACHE_XDG_CACHE_HOST" "$(dirname "$state_path")"
        if [[ "$input_path" == "${DOCS_ROOT}/"* ]]; then
            input_label="${input_path#${DOCS_ROOT}/}"
        else
            input_label="$input_path"
        fi
        if [[ "$output_path" == "${DOCS_ROOT}/"* ]]; then
            output_label="${output_path#${DOCS_ROOT}/}"
        else
            output_label="$output_path"
        fi
        printf '[pandoc] Render %s into %s\n' "$input_label" "$output_label" >&2

        docker run --rm \
            --user "$(id -u):$(id -g)" \
            --volume "${DOCS_ROOT}:${PANDOC_MOUNT_ROOT}" \
            --volume "${REPO_ROOT}:/workspace" \
            --workdir "$PANDOC_MOUNT_ROOT" \
            --env "HOME=${CONTAINER_HOME}" \
            --env "XDG_CACHE_HOME=${CONTAINER_XDG_CACHE}" \
            --env "TEXINPUTS=${CONTAINER_TEXINPUTS}" \
            --env "GENESTACK_DOCS_ROOT=${PANDOC_MOUNT_ROOT}" \
            --env "GENESTACK_REPO_ROOT=/workspace" \
            "$PANDOC_IMAGE" \
            --defaults "$CONTAINER_DEFAULTS" \
            --output "$(container_path "$output_path")" \
            "$(container_path "$input_path")"

        printf '%s\n' "$state_payload" > "$state_path"
        printf '[pdf] built: %s\n' "$output_label"
    done
}

build_all_guides=0
if ((${#GUIDE_TARGETS[@]} == 0)); then
    build_all_guides=1
fi

for guide_target in "${GUIDE_TARGETS[@]}"; do
    if [[ "$guide_target" == "all" ]]; then
        build_all_guides=1
        break
    fi
done

REQUESTED_GUIDES=()
if ((build_all_guides)); then
    mapfile -t REQUESTED_GUIDES < <(load_all_guides)
else
    for guide_target in "${GUIDE_TARGETS[@]}"; do
        if [[ "$guide_target" != "all" ]]; then
            REQUESTED_GUIDES+=("$guide_target")
        fi
    done
fi

CONTAINER_HOME="$(container_path "$CACHE_HOME_HOST")"
CONTAINER_XDG_CACHE="$(container_path "$CACHE_XDG_CACHE_HOST")"
CONTAINER_DEFAULTS="$(container_path "$PANDOC_DEFAULTS")"
CONTAINER_TEXINPUTS="$(build_container_texinputs "$PANDOC_DEFAULTS" "$DOCS_ROOT" "$PANDOC_MOUNT_ROOT")"
export TEXINPUTS="$CONTAINER_TEXINPUTS"

for guide_target in "${REQUESTED_GUIDES[@]}"; do
    mapfile -t PENDING_RENDERS < <(run_assembler "$guide_target")
    render_pending_renders "${PENDING_RENDERS[@]}"
done
