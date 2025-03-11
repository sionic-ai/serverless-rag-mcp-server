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
            "required": ["api_key", "question"],  # 필수: api_key, question
        },
    },
    {
        "name": "list_agents",
        "description": (
            "Bearer 토큰을 사용해 /api/v2/agents GET으로 호출, "
            "현재 로그인 유저(=해당 bearer) 기준의 에이전트 목록을 가져옵니다. "
            "코드에서 환경변수 BEARER_TOKEN을 사용하므로, 인자로 받을 필요는 없습니다."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                # bearer_token을 굳이 넣지 않고, page/size만 옵션
                "page": {
                    "type": "integer",
                    "description": "페이지 번호 (옵션)",
                },
                "size": {
                    "type": "integer",
                    "description": "페이지 크기 (옵션)",
                },
            },
            "required": [],  # 모두 옵션
        },
    },
    {
        "name": "list_buckets",
        "description": (
            "Bearer 토큰을 사용해 /api/v2/buckets GET으로 호출, 특정 에이전트에 등록된 버킷 목록을 조회합니다."
            " 코드상에서는 환경변수 BEARER_TOKEN을 사용하며, 인자로 agent_id만 꼭 필요합니다."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                # bearer_token도 빼거나, 혹은 남겨두되 필수는 아님
                "agent_id": {"type": "string", "description": "조회할 에이전트 ID"},
                "page": {"type": "integer", "description": "페이지 번호 (옵션)"},
                "size": {"type": "integer", "description": "페이지 크기 (옵션)"},
            },
            "required": ["agent_id"],  # agent_id만 필수
        },
    },
    {
        "name": "upload_document_by_file",
        "description": "파일을 /api/v2/documents/by-file 엔드포인트에 업로드",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bucket_id": {
                    "type": "string",
                    "description": "학습된 문서를 저장할 버킷 ID",
                },
                "file_path": {
                    "type": "string",
                    "description": "업로드할 로컬 파일 경로 (옵션)",
                },
                "file_base64": {
                    "type": "string",
                    "description": "Base64 인코딩된 파일 데이터 (옵션)",
                },
                "file_name": {
                    "type": "string",
                    "description": "file_base64를 사용하는 경우, 업로드될 실제 파일 이름 (예: foo.pdf)",
                },
                "webhook_url": {
                    "type": "string",
                    "description": "결과를 받을 웹훅 URL (옵션)",
                },
            },
            "required": [
                "bucket_id"
            ],  # bucket_id는 반드시 필요, file_path 또는 file_base64는 둘 중 하나 이상 있어야 함
        },
    },
]
