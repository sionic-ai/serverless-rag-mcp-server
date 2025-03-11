import requests
from typing import Any, Dict


def call_internal_api(
    method: str,
    endpoint: str,
    storm_api_key: str,
    base_url: str = "https://live-stargate.sionic.im",
    params: Dict[str, Any] = None,
    data: Dict[str, Any] = None,
    files: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    storm-api-key를 사용해 내부 API를 호출하는 공통 헬퍼.
    """
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
