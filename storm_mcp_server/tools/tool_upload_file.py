import mimetypes
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from typing import List, Dict

from storm_mcp_server.core.file_manager import FileSystemManager


class FileServer:
    def __init__(self, base_path):
        self.fs = FileSystemManager(base_path)
        self.server = Server("file-server")

    def setup_handlers(self):
        """MCP 핸들러 설정"""

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            items = await self.fs.list_directory()
            return [
                Resource(
                    uri=f"file:///{item['path']}",
                    name=item["name"],
                    mimeType=(
                        "inode/directory"
                        if item["type"] == "directory"
                        else mimetypes.guess_type(item["name"])[0] or "text/plain"
                    ),
                    description=f"{'Directory' if item['type'] == 'directory' else 'File'}: {item['path']}",
                )
                for item in items
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            path = uri.replace("file:///", "")
            content, _ = await self.fs.read_file(path)
            return content

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="upload_file",
                    description="파일 업로드(Base64 인코딩된 컨텐츠)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "업로드할 파일 경로(서버 내)",
                            },
                            "fileContent": {
                                "type": "string",
                                "description": "Base64 인코딩된 파일 내용",
                            },
                        },
                        "required": ["path", "fileContent"],
                    },
                ),
                Tool(
                    name="search_files",
                    description="파일 검색",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "검색할 키워드",
                            }
                        },
                        "required": ["pattern"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict) -> List[TextContent]:
            if name == "upload_file":
                # 파일 업로드
                path = arguments["path"]
                b64_content = arguments["fileContent"]

                await self.fs.upload_file(path, b64_content)
                return [
                    TextContent(type="text", text=f"File uploaded successfully: {path}")
                ]

            elif name == "search_files":
                # 파일 검색
                pattern = arguments["pattern"]
                results = await self.fs.search_files(pattern)
                if not results:
                    return [TextContent(type="text", text="No files found")]

                text_output = "\n".join(f"[{r['type']}] {r['path']}" for r in results)
                return [TextContent(type="text", text=text_output)]

            raise ValueError(f"Unknown tool: {name}")
