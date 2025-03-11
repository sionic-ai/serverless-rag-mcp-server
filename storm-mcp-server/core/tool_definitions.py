# https://sionic-storm-openapi.apidog.io/api-10613460

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
                    "description": "storm-api-key 헤더로 보낼 API 키",
                },
                "question": {"type": "string", "description": "채팅 질문 텍스트"},
                "bucketIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "질문 대상 버킷 ID 리스트 (옵션)",
                },
                "threadId": {
                    "type": "string",
                    "description": "채팅을 전송할 스레드 ID (옵션)",
                },
                "webhookUrl": {
                    "type": "string",
                    "description": "결과를 받을 웹훅 URL (옵션)",
                },
            },
            "required": ["api_key", "question"],
        },
    },
    {
        "name": "list_agents",
        "description": (
            "Bearer 토큰을 사용해 /api/v2/agents GET 으로 호출, "
            "현재 로그인 유저(=해당 bearer) 기준의 에이전트 목록을 가져옵니다."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "bearer_token": {
                    "type": "string",
                    "description": "인증에 사용할 Bearer 토큰",
                },
                "page": {"type": "integer", "description": "페이지 번호 (옵션)"},
                "size": {"type": "integer", "description": "페이지 크기 (옵션)"},
            },
            "required": ["bearer_token"],
        },
    },
    {
        "name": "list_buckets",
        "description": (
            "Bearer 토큰을 사용해 /api/v2/buckets GET 으로 호출, 특정 에이전트에 등록된 버킷 목록을 조회합니다."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "bearer_token": {
                    "type": "string",
                    "description": "인증에 사용할 Bearer 토큰",
                },
                "agent_id": {"type": "string", "description": "조회할 에이전트 ID"},
                "page": {"type": "integer", "description": "페이지 번호 (옵션)"},
                "size": {"type": "integer", "description": "페이지 크기 (옵션)"},
            },
            "required": ["bearer_token", "agent_id"],
        },
    },
    {
        "name": "upload_document_by_file",
        "description": (
            "Bearer 토큰을 사용해 /api/v2/documents/by-file 에 문서를 업로드(학습)합니다. "
            "multipart/form-data 로 bucketId, file 등을 전송."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "bearer_token": {
                    "type": "string",
                    "description": "인증에 사용할 Bearer 토큰",
                },
                "bucket_id": {
                    "type": "string",
                    "description": "학습된 문서를 저장할 버킷 ID",
                },
                "file_path": {
                    "type": "string",
                    "description": "업로드할 로컬 파일 경로",
                },
                "webhook_url": {
                    "type": "string",
                    "description": "결과를 받을 웹훅 URL (옵션)",
                },
            },
            "required": ["bearer_token", "bucket_id", "file_path"],
        },
    },
]
