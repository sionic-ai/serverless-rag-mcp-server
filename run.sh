#!/bin/bash

# 현재 실행 중인 스크립트(.sh) 파일이 위치한 디렉터리를 찾아 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# MCP 프로토콜상 stdout에는 JSON만 내보내야 하므로,
# 상태/디버그 메시지는 stderr로 리다이렉트
echo "Current directory: $(pwd)" 1>&2
echo "Listing contents:" 1>&2
ls -la 1>&2

# MCP 서버(Python 스크립트) 실행
uv run ./hello.py
