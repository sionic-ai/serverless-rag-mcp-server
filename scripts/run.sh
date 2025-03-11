#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$ROOT_DIR"

echo "Current directory: $(pwd)" 1>&2
ls -la 1>&2

export STORM_API_KEY='st_78b9ad250b9f403e82f6caa4f49f3453'

# ★ 'uv run' 대신 'python -m' 사용:
uv run -m storm_mcp_server.main
