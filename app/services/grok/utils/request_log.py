"""
Token 最后一次请求记录（纯内存，重启丢失）
"""

from datetime import datetime
from typing import Any, Dict, Optional


# token → 最后一次请求详情
_last_requests: Dict[str, Dict[str, Any]] = {}


def record(
    token: str,
    *,
    url: str,
    method: str,
    request_headers: Dict[str, str],
    request_body: Any,
    status_code: int,
    response_headers: Dict[str, str],
    response_body: str,
) -> None:
    """记录某个 token 的最后一次 HTTP 请求详情。"""
    raw_token = token.replace("sso=", "")
    _last_requests[raw_token] = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "method": method,
        "request_headers": request_headers,
        "request_body": request_body,
        "status_code": status_code,
        "response_headers": response_headers,
        "response_body": response_body,
    }


def get(token: str) -> Optional[Dict[str, Any]]:
    """获取某个 token 的最后一次请求记录。"""
    raw_token = token.replace("sso=", "")
    return _last_requests.get(raw_token)


__all__ = ["record", "get"]
