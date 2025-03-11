.PHONY: format check

format:
	ruff format storm-mcp-server

check:
	ruff check storm-mcp-server

run:
	sh ./scripts/run.sh
