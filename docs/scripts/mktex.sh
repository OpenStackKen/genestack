#!/usr/bin/env bash
set -euo pipefail

# This wrapper mirrors mkpdf.sh's guide-selection and container contract, but
# it stops at Pandoc's LaTeX output so generated `.tex` can be inspected
# directly when debugging PDF failures.

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

paths: list[str] = []
in_resource_path = False
for raw_line in defaults_path.read_text(encoding="utf-8").splitlines():
    stripped = raw_line.strip()

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

build_host_texinputs() {
    local defaults_path="$1"
    local docs_root="$2"

    "$PYTHON" - "$defaults_path" "$docs_root" <<'PY'
from pathlib import Path
import sys

defaults_path = Path(sys.argv[1]).resolve()
docs_root = Path(sys.argv[2]).resolve()

paths: list[str] = []
in_resource_path = False
for raw_line in defaults_path.read_text(encoding="utf-8").splitlines():
    stripped = raw_line.strip()

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
            paths.append(resource_path.as_posix())
        else:
            paths.append((docs_root / resource_path).resolve().as_posix())
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

derive_tex_output_path() {
    "$PYTHON" - "$DOCS_ROOT" "$OUTPUT_ROOT" "$1" <<'PY'
from pathlib import Path
import sys

docs_root = Path(sys.argv[1]).resolve()
output_root = Path(sys.argv[2]).resolve()
pdf_output = Path(sys.argv[3]).resolve()

relative = pdf_output.relative_to(output_root)
tex_output = output_root / "temp" / "tex" / relative.parent / f"{pdf_output.stem}.tex"
print(tex_output)
PY
}

rewrite_tex_paths_for_host() {
    local tex_output_path="$1"

    "$PYTHON" - "$DOCS_ROOT" "$REPO_ROOT" "$OUTPUT_ROOT" "$tex_output_path" "$PANDOC_MOUNT_ROOT" <<'PY'
from pathlib import Path
import sys

docs_root = Path(sys.argv[1]).resolve()
repo_root = Path(sys.argv[2]).resolve()
output_root = Path(sys.argv[3]).resolve()
tex_path = Path(sys.argv[4]).resolve()
mount_root = sys.argv[5].rstrip("/") or "/docs"

text = tex_path.read_text(encoding="utf-8")
text = text.replace(f"{mount_root}/", docs_root.as_posix().rstrip("/") + "/")
text = text.replace("/workspace/", repo_root.as_posix().rstrip("/") + "/")
text = text.replace("./pdf/", output_root.as_posix().rstrip("/") + "/")
tex_path.write_text(text, encoding="utf-8")
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
print(output_dir)
print(output_dir / "temp" / "home")
print(output_dir / "temp" / "xdg-cache")
PY
)

PANDOC_DEFAULTS="$(resolve_docs_path "${PANDOC_DEFAULTS_OVERRIDE:-${CONFIG_VALUES[0]}}")"
PANDOC_IMAGE="${PANDOC_IMAGE_OVERRIDE:-${CONFIG_VALUES[1]}}"
PANDOC_MOUNT_ROOT="${PANDOC_MOUNT_ROOT_OVERRIDE:-${CONFIG_VALUES[2]}}"
OUTPUT_ROOT="$(resolve_docs_path "${CONFIG_VALUES[3]}")"
CACHE_HOME_HOST="$(resolve_docs_path "${CACHE_HOME_OVERRIDE:-${CONFIG_VALUES[4]}}")"
CACHE_XDG_CACHE_HOST="$(resolve_docs_path "${CACHE_XDG_CACHE_OVERRIDE:-${CONFIG_VALUES[5]}}")"
TEX_CACHE_ROOT="${OUTPUT_ROOT}/temp/tex"

if ((CLEAN_REQUESTED)); then
    rm -rf "$TEX_CACHE_ROOT"
    exit 0
fi

if ! docker image inspect "$PANDOC_IMAGE" >/dev/null 2>&1; then
    printf '[tex] missing image: %s\n' "$PANDOC_IMAGE" >&2
    printf '[tex] run `make -C %s deps` before invoking the TeX builder\n' "$DOCS_ROOT" >&2
    exit 1
fi

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

run_assembler() {
    "$PYTHON" "$ASSEMBLER" "${ASSEMBLER_ARGS[@]}" "$@"
}

render_from_guide() {
    local guide_target="$1"
    local input_path pdf_output_path tex_output_path
    local input_label tex_label

    input_path="${OUTPUT_ROOT}/temp/build/${guide_target}.md"
    pdf_output_path="${OUTPUT_ROOT}/${guide_target}.pdf"
    tex_output_path="$(derive_tex_output_path "$pdf_output_path")"

    if [[ ! -f "$input_path" ]]; then
        printf '[tex] missing assembled input: %s\n' "$input_path" >&2
        exit 1
    fi

    mkdir -p "$CACHE_HOME_HOST" "$CACHE_XDG_CACHE_HOST" "$(dirname "$tex_output_path")"

    if [[ "$input_path" == "${DOCS_ROOT}/"* ]]; then
        input_label="${input_path#${DOCS_ROOT}/}"
    else
        input_label="$input_path"
    fi
    if [[ "$tex_output_path" == "${DOCS_ROOT}/"* ]]; then
        tex_label="${tex_output_path#${DOCS_ROOT}/}"
    else
        tex_label="$tex_output_path"
    fi

    printf '[pandoc] Render %s into %s\n' "$input_label" "$tex_label" >&2

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
        --to latex \
        --output "$(container_path "$tex_output_path")" \
        "$(container_path "$input_path")"

    rewrite_tex_paths_for_host "$tex_output_path"
    printf '[tex] built: %s\n' "$tex_label"
    printf 'TEXINPUTS="%s"\n' "$HOST_TEXINPUTS"
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
HOST_TEXINPUTS="$(build_host_texinputs "$PANDOC_DEFAULTS" "$DOCS_ROOT")"
export TEXINPUTS="$CONTAINER_TEXINPUTS"

for guide_target in "${REQUESTED_GUIDES[@]}"; do
    run_assembler "$guide_target" >/dev/null
    render_from_guide "$guide_target"
done
