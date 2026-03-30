#!/usr/bin/env bash

set -euo pipefail

# This generator is intentionally docs-specific: it translates the legacy reno
# + pandoc release-note flow into a Hugo-ready content page while preserving
# the current content-tree location and required front matter.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/../.." && pwd)"
docs_root="${repo_root}/docs"
output_file="${docs_root}/content/overview/release-notes.md"
tmp_dir="${docs_root}/tmp"

mkdir -p "${tmp_dir}"

rst_tmp="$(mktemp "${tmp_dir}/reno.XXXXXX.rst")"
md_tmp="$(mktemp "${tmp_dir}/reno.XXXXXX.md")"
page_tmp="$(mktemp "${tmp_dir}/release-notes.XXXXXX.md")"

cleanup() {
  rm -f "${rst_tmp}" "${md_tmp}" "${page_tmp}"
}
trap cleanup EXIT

cd "${repo_root}"
reno report -o "${rst_tmp}"
pandoc "${rst_tmp}" -f rst --shift-heading-level-by=1 -V title:"" -t gfm-raw_html -o "${md_tmp}"

cat > "${page_tmp}" <<'EOF'
---
title: "Release Notes"
weight: 50
---
EOF

cat "${md_tmp}" >> "${page_tmp}"
mv "${page_tmp}" "${output_file}"
