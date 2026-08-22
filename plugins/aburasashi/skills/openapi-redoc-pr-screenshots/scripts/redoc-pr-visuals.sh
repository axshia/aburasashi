#!/usr/bin/env bash
set -euo pipefail

skill_script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
runtime_base="${ABURASASHI_REDOC_RUNTIME_DIR:-${XDG_CACHE_HOME:-${HOME}/.cache}/aburasashi/openapi-redoc-pr-screenshots}"
runtime_dir="${runtime_base}/redocly-2.47.0-playwright-1.62.1"
redocly_bin="${runtime_dir}/node_modules/.bin/redocly"
playwright_bin="${runtime_dir}/node_modules/.bin/playwright"

if [[ ! -x "${redocly_bin}" || ! -x "${playwright_bin}" ]]; then
  mkdir -p "${runtime_dir}"
  npm install \
    --prefix "${runtime_dir}" \
    --no-save \
    --no-package-lock \
    --no-audit \
    --no-fund \
    @redocly/cli@2.47.0 \
    playwright@1.62.1
fi

export NODE_PATH="${runtime_dir}/node_modules"
export ABURASASHI_REDOC_BIN="${redocly_bin}"
export ABURASASHI_PLAYWRIGHT_BIN="${playwright_bin}"
export PLAYWRIGHT_BROWSERS_PATH="${runtime_dir}/browsers"

exec node "${skill_script_dir}/redoc-pr-visuals.cjs" "$@"
