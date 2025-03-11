.PHONY: format check

format:
	ruff format storm_mcp_server

check:
	ruff check storm_mcp_server

run:
	sh ./scripts/run.sh
