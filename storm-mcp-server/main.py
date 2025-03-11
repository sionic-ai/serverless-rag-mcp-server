import asyncio
from mcp.server.stdio import stdio_server
from core.tool_server import server


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    print(f"Starting {__name__}")

    asyncio.run(main())
