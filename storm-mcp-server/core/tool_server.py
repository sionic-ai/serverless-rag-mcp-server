from mcp.server import Server
from .tool_handlers import handle_list_tools, handle_call_tool

# MCP 서버 인스턴스 생성
server = Server("storm-platform")

# --------------------------------------------------------------------------
# 1) MCP 쪽에서 'tools/list' 이벤트가 들어오면
#    handle_list_tools 함수를 호출하도록 등록
# --------------------------------------------------------------------------
server.list_tools()(handle_list_tools)

# --------------------------------------------------------------------------
# 2) MCP 쪽에서 'tool/call' 이벤트가 들어오면
#    handle_call_tool 함수를 호출하도록 등록
# --------------------------------------------------------------------------
server.call_tool()(handle_call_tool)
