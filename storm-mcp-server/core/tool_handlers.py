import asyncio
import json
from typing import List, Dict, Any
from mcp.types import Tool, TextContent

from core.tool_definitions import TOOLS_DEFINITION
from .chat_api import call_chat_api
from .internal_api import call_internal_api


async def handle_list_tools() -> List[Tool]:
    tool_objects: List[Tool] = []
    for tdef in TOOLS_DEFINITION:
        tool_objects.append(
            Tool(
                name=tdef["name"],
                description=tdef["description"],
                inputSchema=tdef["inputSchema"],
            )
        )
    return tool_objects


async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    MCP에서 'tool/call' 이벤트로 특정 툴(name)을 호출하면,
    여기서 그 이름에 맞게 실제 비즈니스 로직(call_chat_api, call_internal_api 등)을 실행.

    반환값은 List[TextContent] 형태여야 하며, MCP에 문자열 형태로 전달된다.
    """
    try:
        if name == "send_nonstream_chat":
            # ---------------------
            # 1) /api/v2/answer (non-stream) 호출 (Storm API Key)
            # ---------------------
            api_key = arguments.get("api_key", "").strip()
            question = arguments.get("question", "").strip()
            bucket_ids = arguments.get("bucketIds", None)
            thread_id = arguments.get("threadId", None)
            webhook_url = arguments.get("webhookUrl", None)

            if not api_key:
                raise ValueError("api_key is required")
            if not question:
                raise ValueError("question is required")

            response_data = await asyncio.to_thread(
                call_chat_api,
                api_key=api_key,
                question=question,
                bucket_ids=bucket_ids,
                thread_id=thread_id,
                webhook_url=webhook_url,
            )
            result_text = json.dumps(response_data, ensure_ascii=False, indent=2)
            return [TextContent(type="text", text=result_text)]

        elif name == "list_agents":
            # ---------------------
            # 2) /api/v2/agents (GET) Bearer 토큰 인증
            # ---------------------
            bearer_token = arguments.get("bearer_token", "").strip()
            page = arguments.get("page", None)
            size = arguments.get("size", None)

            if not bearer_token:
                raise ValueError("bearer_token is required")

            params = {}
            if page is not None:
                params["page"] = page
            if size is not None:
                params["size"] = size

            response_data = await asyncio.to_thread(
                call_internal_api,
                method="GET",
                endpoint="/api/v2/agents",
                bearer_token=bearer_token,
                params=params,
            )
            result_text = json.dumps(response_data, ensure_ascii=False, indent=2)
            return [TextContent(type="text", text=result_text)]

        elif name == "list_buckets":
            # ---------------------
            # 3) /api/v2/buckets (GET) Bearer 토큰 인증
            # ---------------------
            bearer_token = arguments.get("bearer_token", "").strip()
            agent_id = arguments.get("agent_id", "").strip()
            page = arguments.get("page", None)
            size = arguments.get("size", None)

            if not bearer_token:
                raise ValueError("bearer_token is required")
            if not agent_id:
                raise ValueError("agent_id is required")

            params = {"agentId": agent_id}
            if page is not None:
                params["page"] = page
            if size is not None:
                params["size"] = size

            response_data = await asyncio.to_thread(
                call_internal_api,
                method="GET",
                endpoint="/api/v2/buckets",
                bearer_token=bearer_token,
                params=params,
            )
            result_text = json.dumps(response_data, ensure_ascii=False, indent=2)
            return [TextContent(type="text", text=result_text)]

        elif name == "upload_document_by_file":
            # ---------------------
            # 4) /api/v2/documents/by-file (POST) Bearer + multipart
            # ---------------------
            bearer_token = arguments.get("bearer_token", "").strip()
            bucket_id = arguments.get("bucket_id", "").strip()
            file_path = arguments.get("file_path", "").strip()
            webhook_url = arguments.get("webhook_url", None)

            if not bearer_token:
                raise ValueError("bearer_token is required")
            if not bucket_id:
                raise ValueError("bucket_id is required")
            if not file_path:
                raise ValueError("file_path is required")

            data = {"bucketId": bucket_id}
            if webhook_url:
                data["webhookUrl"] = webhook_url

            # 파일을 읽어들여 multipart로 전송
            with open(file_path, "rb") as f:
                files = {"file": (file_path, f, "application/octet-stream")}
                response_data = await asyncio.to_thread(
                    call_internal_api,
                    method="POST",
                    endpoint="/api/v2/documents/by-file",
                    bearer_token=bearer_token,
                    data=data,
                    files=files,
                )

            result_text = json.dumps(response_data, ensure_ascii=False, indent=2)
            return [TextContent(type="text", text=result_text)]

        else:
            raise ValueError(f"Tool '{name}' not found.")

    except Exception as e:
        # 에러 발생 시 MCP 쪽에 오류 메시지를 전달하기 위해 RuntimeError로 래핑
        raise RuntimeError(f"Tool call error: {str(e)}") from e
