import asyncio
import base64
import json
from io import BytesIO
from typing import List, Dict, Any
from mcp.types import Tool, TextContent

from storm_mcp_server.core.internal_api import call_internal_api, call_chat_api
from storm_mcp_server.tools.tool_definitions import TOOLS_DEFINITION


async def handle_list_tools() -> List[Tool]:
    """
    MCP에서 'tools/list' 이벤트가 오면,
    우리가 보유한 툴(TOOLS_DEFINITION)을 반환.
    """
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
            # --------------------------------------------------------
            # (1) /api/v2/answer (non-stream) - Storm API Key 기반
            # --------------------------------------------------------
            question = arguments.get("question", "").strip()
            bucket_ids = arguments.get("bucketIds", None)
            thread_id = arguments.get("threadId", None)
            webhook_url = arguments.get("webhookUrl", None)

            if not question:
                raise ValueError("question is required")

            # 실제 호출
            response_data = await asyncio.to_thread(
                call_chat_api,
                question=question,
                bucket_ids=bucket_ids,
                thread_id=thread_id,
                webhook_url=webhook_url,
            )
            result_text = json.dumps(response_data, ensure_ascii=False, indent=2)
            return [TextContent(type="text", text=result_text)]

        elif name == "list_agents":
            page = arguments.get("page", None)
            size = arguments.get("size", None)

            params = {}
            if page is not None:
                params["page"] = page
            if size is not None:
                params["size"] = size

            response_data = await asyncio.to_thread(
                call_internal_api,
                method="GET",
                endpoint="/api/v2/agents",
                params=params,
            )
            result_text = json.dumps(response_data, ensure_ascii=False, indent=2)
            return [TextContent(type="text", text=result_text)]

        elif name == "list_buckets":
            # --------------------------------------------------------
            # (3) /api/v2/buckets (GET) - Storm API Key
            # --------------------------------------------------------
            agent_id = arguments.get("agent_id", "").strip()
            if not agent_id:
                raise ValueError("agent_id is required")

            page = arguments.get("page", None)
            size = arguments.get("size", None)

            params = {"agentId": agent_id}
            if page is not None:
                params["page"] = page
            if size is not None:
                params["size"] = size

            response_data = await asyncio.to_thread(
                call_internal_api,
                method="GET",
                endpoint="/api/v2/buckets",
                params=params,
            )
            result_text = json.dumps(response_data, ensure_ascii=False, indent=2)
            return [TextContent(type="text", text=result_text)]

        elif name == "upload_document_by_file":
            # --------------------------------------------------------

            #  /api/v2/documents/by-file (POST)

            #   - file_path (로컬 경로)

            #   - file_base64 (Base64)

            #   - file_name (Base64 시 파일명)

            # --------------------------------------------------------

            bucket_id = arguments.get("bucket_id", "").strip()

            file_path = arguments.get("file_path", "").strip()

            file_base64 = arguments.get("file_base64", None)

            file_name = arguments.get("file_name", None)

            webhook_url = arguments.get("webhook_url", None)

            if not bucket_id:
                raise ValueError("bucket_id is required")

            # file_path, file_base64 둘 다 없으면 에러

            if not file_path and not file_base64:
                raise ValueError("Either file_path or file_base64 must be provided")

            data = {"bucketId": bucket_id}

            if webhook_url:
                data["webhookUrl"] = webhook_url

            # ---------------------------

            # 1) file_path 있는 경우 → 로컬 파일 열기

            # ---------------------------

            if file_path:
                # 로컬 파일 읽어 multipart 전송

                with open(file_path, "rb") as f:
                    # MIME 타입은 일단 "application/octet-stream"으로 가정

                    files = {"file": (file_path, f, "application/octet-stream")}

                    response_data = await asyncio.to_thread(
                        call_internal_api,
                        method="POST",
                        endpoint="/api/v2/documents/by-file",
                        data=data,
                        files=files,
                    )

            # ---------------------------

            # 2) file_base64 있는 경우 → 메모리에서 BytesIO

            # ---------------------------

            else:
                # file_name이 없으면 기본 이름 "uploaded_file"

                if not file_name:
                    file_name = "uploaded_file"

                raw_data = base64.b64decode(file_base64)

                file_obj = BytesIO(raw_data)

                # 마찬가지로 MIME 타입은 "application/octet-stream" 기본

                files = {"file": (file_name, file_obj, "application/octet-stream")}

                response_data = await asyncio.to_thread(
                    call_internal_api,
                    method="POST",
                    endpoint="/api/v2/documents/by-file",
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
