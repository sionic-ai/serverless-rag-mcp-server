#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$ROOT_DIR"

echo "Current directory: $(pwd)" 1>&2
ls -la 1>&2

# 아래에 Storm API KEY를 입력하세요.
export STORM_API_KEY=''

# ★ 'uv run' 대신 'python -m' 사용:
uv run -m storm_mcp_server.main
