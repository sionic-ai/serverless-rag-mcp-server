import requests
from typing import Any, Dict


def call_internal_api(
    method: str,
    endpoint: str,
    bearer_token: str,
    base_url: str = "https://live-stargate.sionic.im",
    params: Dict[str, Any] = None,
    data: Dict[str, Any] = None,
    files: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Bearer 토큰을 포함해 내부 API를 호출하는 공통 헬퍼.
      - method: "GET" | "POST" | "DELETE" 등
      - endpoint: 예) "/api/v2/agents"
      - bearer_token: "eyJhbGciOiJIUz..." 형태
      - params: GET query 등에 쓰일 파라미터
      - data: POST body 등에 쓰일 form data (json 아님)
      - files: 멀티파트 업로드 시 사용
    """
    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    # 메서드별 분기
    if method.upper() == "GET":
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    elif method.upper() == "POST":
        if files:
            # 멀티파트 전송
            resp = requests.post(
                url, headers=headers, data=data, files=files, timeout=60
            )
        else:
            # 일반 JSON POST
            headers["Content-Type"] = "application/json"
            resp = requests.post(
                url, headers=headers, json=data, params=params, timeout=30
            )
    elif method.upper() == "DELETE":
        resp = requests.delete(url, headers=headers, params=params, timeout=30)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    if resp.status_code >= 400:
        raise Exception(f"API error: {resp.status_code} - {resp.text}")

    # 일부 API의 응답이 text/plain일 수 있으므로, JSON 변환 시도
    try:
        return resp.json()
    except Exception:
        return {"status": "success", "data": resp.text}
