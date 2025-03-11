import requests
from typing import Any, Dict, List


def call_chat_api(
    api_key: str,
    question: str,
    bucket_ids: List[str] = None,
    thread_id: str = None,
    webhook_url: str = None,
    base_url: str = "https://live-stargate.sionic.im",
) -> Dict[str, Any]:
    """
    /api/v2/answer (non-stream) 호출 예시
    - header: storm-api-key: {api_key}
    - body: { "question": "...", "bucketIds": [...], "threadId": "...", "webhookUrl": "..." }
    """
    url = f"{base_url}/api/v2/answer"
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
