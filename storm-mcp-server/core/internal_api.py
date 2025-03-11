import os

import requests
from typing import Any, Dict, List


def call_internal_api(
    method: str,
    endpoint: str,
    base_url: str = "https://live-stargate.sionic.im",
    params: Dict[str, Any] = None,
    data: Dict[str, Any] = None,
    files: Dict[str, Any] = None,
) -> Dict[str, Any]:
    storm_api_key = os.getenv("STORM_API_KEY")
    url = f"{base_url}{endpoint}"
    headers = {"Content-Type": "application/json", "storm-api-key": storm_api_key}

    if method.upper() == "GET":
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    elif method.upper() == "POST":
        if files:
            # 멀티파트
            resp = requests.post(
                url, headers=headers, data=data, files=files, timeout=60
            )
        else:
            resp = requests.post(
                url, headers=headers, json=data, params=params, timeout=30
            )
    elif method.upper() == "DELETE":
        resp = requests.delete(url, headers=headers, params=params, timeout=30)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    if resp.status_code >= 400:
        raise Exception(f"API error: {resp.status_code} - {resp.text}")

    # text/plain 응답 대비
    try:
        return resp.json()
    except Exception:
        return {"status": "success", "data": resp.text}


def call_chat_api(
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
    storm_api_key = os.getenv("STORM_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "storm-api-key": storm_api_key,
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
