import json
import asyncio
import requests
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# MCP 서버 인스턴스 생성
server = Server("chat-api-v2-answer")

#================================================================
# 1) Storm API 호출 헬퍼 함수
#================================================================
def call_chat_api(
    api_key: str,
    question: str,
    bucket_ids: List[str] = None,
    thread_id: str = None,
    webhook_url: str = None,
) -> Dict[str, Any]:
    """
    /api/v2/answer (non-stream) 호출 예시
    - header: storm-api-key: {api_key}
    - body: { "question": "...", "bucketIds": [...], "threadId": "...", "webhookUrl": "..." }
    """
    url = "https://live-stargate.sionic.im/api/v2/answer"  # 사용자 환경에 맞게 수정 가능
    headers = {
        "Content-Type": "application/json",
        "storm-api-key": api_key,  # <-- 헤더 이름이 'storm-api-key'
    }

    body = {
        "question": question,
    }
    if bucket_ids:
        body["bucketIds"] = bucket_ids
    if thread_id:
        body["threadId"] = thread_id
    if webhook_url:
        body["webhookUrl"] = webhook_url

    response = requests.post(url, headers=headers, json=body, timeout=30)

    if response.status_code >= 400:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    return response.json()

#================================================================
# 2) MCP Tool 정의
#================================================================
TOOLS_DEFINITION = [
    {
        "name": "send_nonstream_chat",
        "description": (
            "/api/v2/answer (non-stream)로 POST 요청을 보내어 질문(question)에 대한 "
            "답변을 받아옵니다. (storm-api-key 헤더 사용)"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "storm-api-key 헤더로 보낼 API 키"
                },
                "question": {
                    "type": "string",
                    "description": "채팅 질문 텍스트"
                },
                "bucketIds": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "질문 대상 버킷 ID 리스트 (옵션)"
                },
                "threadId": {
                    "type": "string",
                    "description": "채팅을 전송할 스레드 ID (옵션)"
                },
                "webhookUrl": {
                    "type": "string",
                    "description": "결과를 받을 웹훅 URL (옵션)"
                }
            },
            "required": ["api_key", "question"]  # 최소 필드는 api_key, question
        }
    }
]

#================================================================
# 3) list_tools 핸들러
#================================================================
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """MCP가 'tools/list'를 호출하면 이 핸들러가 실행됩니다."""
    tool_objects: List[Tool] = []
    for tdef in TOOLS_DEFINITION:
        tool_objects.append(
            Tool(
                name=tdef["name"],
                description=tdef["description"],
                inputSchema=tdef["inputSchema"]
            )
        )
    return tool_objects

#================================================================
# 4) call_tool 핸들러
#================================================================
@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        if name != "send_nonstream_chat":
            raise ValueError(f"Tool '{name}' not found.")

        # 파라미터 꺼내기
        api_key = arguments.get("api_key", "").strip()
        question = arguments.get("question", "").strip()
        bucket_ids = arguments.get("bucketIds", None)
        thread_id = arguments.get("threadId", None)
        webhook_url = arguments.get("webhookUrl", None)

        if not api_key:
            raise ValueError("api_key is required")
        if not question:
            raise ValueError("question is required")

        # 비동기로 동기 함수를 감싸기
        response_data = await asyncio.to_thread(
            call_chat_api,
            api_key=api_key,
            question=question,
            bucket_ids=bucket_ids,
            thread_id=thread_id,
            webhook_url=webhook_url
        )

        # Storm API 응답을 JSON 텍스트로 변환해 MCP TextContent로 감싸기
        result_text = json.dumps(response_data, ensure_ascii=False, indent=2)
        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        raise RuntimeError(f"Tool call error: {str(e)}") from e

#================================================================
# 5) 서버 실행 진입점
#================================================================
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
