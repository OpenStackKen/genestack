#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/../.." && pwd)

INPUT_FILE="${REPO_ROOT}/helm-chart-versions.yaml"
OUTPUT_FILE="${REPO_ROOT}/docs/content/overview/product-matrix.md"
OUTPUT_DIR=$(dirname "${OUTPUT_FILE}")

if ! command -v awk >/dev/null 2>&1; then
    echo "Error: awk is required to generate the product matrix." >&2
    exit 1
fi

if [[ ! -f "${INPUT_FILE}" ]]; then
    echo "Error: Required file not found: ${INPUT_FILE}" >&2
    exit 1
fi

charts=$(
    awk '
        /^charts:[[:space:]]*$/ { in_charts=1; next }
        in_charts && /^[^[:space:]]/ { exit }
        in_charts && /^  [^:#][^:]*:[[:space:]]*/ {
            line = substr($0, 3)
            key = line
            sub(/:.*/, "", key)
            value = line
            sub(/^[^:]*:[[:space:]]*/, "", value)
            if (key != "" && value != "") {
                printf "%s\t%s\n", key, value
            }
        }
    ' "${INPUT_FILE}" | LC_ALL=C sort
)

if [[ -z "${charts}" ]]; then
    echo "Error: 'charts' key not found in ${INPUT_FILE}" >&2
    exit 1
fi

mkdir -p "${OUTPUT_DIR}"

tmp_file=$(mktemp "${OUTPUT_DIR}/product-matrix.md.XXXXXX")
trap 'rm -f "${tmp_file}"' EXIT

cat > "${tmp_file}" <<'EOF'
---
title: "Product Matrix"
weight: 50
---
This matrix is automatically generated from `helm-chart-versions.yaml` at build time.

| Chart Name | Version |
| :--- | :--- |
EOF

while IFS=$'\t' read -r chart version; do
    printf '| **%s** | `%s` |\n' "${chart}" "${version}" >> "${tmp_file}"
done <<< "${charts}"

mv "${tmp_file}" "${OUTPUT_FILE}"
trap - EXIT

echo "Successfully generated product matrix and saved to ${OUTPUT_FILE}"
