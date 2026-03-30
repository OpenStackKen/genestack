#!/usr/bin/env bash

set -euo pipefail

# Resolve the repo root from the script location so callers can invoke the
# wrapper from anywhere. The container always mounts the whole repo because the
# docs build reads shared content and helper scripts from outside /docs.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/../.." && pwd)"
docs_root="${repo_root}/docs"

image="${DOCS_BUILD_IMAGE:-genestack-docs-build:local}"
container_workdir="${DOCS_CONTAINER_WORKDIR:-/workspace/docs}"
host_uid="${HOST_UID:-$(id -u)}"
host_gid="${HOST_GID:-$(id -g)}"
container_flags=()

# Most docs build targets are non-interactive and should not allocate a TTY.
# The shell target, however, needs an interactive container session. Allow the
# caller to request that explicitly without forcing TTY allocation for every
# build or lint command.
if [[ "${DOCS_CONTAINER_INTERACTIVE:-0}" == "1" ]]; then
  if [[ -t 0 && -t 1 ]]; then
    container_flags+=(-it)
  else
    container_flags+=(-i)
  fi
fi

# Keep every cache and generated dependency directory inside /docs so container
# runs remain reproducible, inspectable, and easy to clean with normal repo
# tooling. These locations are intentionally gitignored.
mkdir -p \
  "${docs_root}/.cache/go-build" \
  "${docs_root}/.cache/go-mod" \
  "${docs_root}/.cache/hugo" \
  "${docs_root}/.cache/pip" \
  "${docs_root}/.npm-cache" \
  "${docs_root}/.tmp-home" \
  "${docs_root}/node_modules"

exec docker run --rm \
  "${container_flags[@]}" \
  --user "${host_uid}:${host_gid}" \
  --workdir "${container_workdir}" \
  -e HOME="${container_workdir}/.tmp-home" \
  -e XDG_CACHE_HOME="${container_workdir}/.cache" \
  -e NPM_CONFIG_CACHE="${container_workdir}/.npm-cache" \
  -e npm_config_cache="${container_workdir}/.npm-cache" \
  -e GOCACHE="${container_workdir}/.cache/go-build" \
  -e GOMODCACHE="${container_workdir}/.cache/go-mod" \
  -e HUGO_CACHEDIR="${container_workdir}/.cache/hugo" \
  -e PIP_CACHE_DIR="${container_workdir}/.cache/pip" \
  -v "${repo_root}:/workspace" \
  "${image}" \
  "$@"
