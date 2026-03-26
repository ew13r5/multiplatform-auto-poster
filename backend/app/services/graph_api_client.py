import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class GraphAPIResponse:
    """Structured response from Graph API requests."""
    success: bool
    data: Optional[dict] = None
    error_code: Optional[int] = None
    error_subcode: Optional[int] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    is_retriable: bool = False


def _parse_app_usage(headers: httpx.Headers) -> None:
    """Parse X-App-Usage header and log warning if any metric >80%."""
    usage_str = headers.get("x-app-usage")
    if not usage_str:
        return
    try:
        usage = json.loads(usage_str)
        call_count = usage.get("call_count", 0)
        total_cputime = usage.get("total_cputime", 0)
        total_time = usage.get("total_time", 0)
        if any(v > 80 for v in [call_count, total_cputime, total_time]):
            logger.warning(
                "Graph API usage high: call_count=%s, total_cputime=%s, total_time=%s",
                call_count, total_cputime, total_time,
            )
    except (json.JSONDecodeError, TypeError):
        pass


async def graph_api_request(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    access_token: str,
    params: Optional[dict] = None,
    data: Optional[dict] = None,
) -> GraphAPIResponse:
    """Make an authenticated Graph API request. Returns parsed GraphAPIResponse."""
    request_params = dict(params or {})
    request_params["access_token"] = access_token

    try:
        response = await client.request(method, endpoint, params=request_params, data=data)
    except httpx.TimeoutException:
        return GraphAPIResponse(
            success=False,
            error_message="Request timed out",
            is_retriable=True,
        )
    except httpx.ConnectError:
        return GraphAPIResponse(
            success=False,
            error_message="Connection failed",
            is_retriable=True,
        )

    _parse_app_usage(response.headers)

    try:
        body = response.json()
    except Exception:
        return GraphAPIResponse(
            success=False,
            error_message=f"Invalid JSON response: {response.text[:200]}",
        )

    if "error" in body:
        error = body["error"]
        return GraphAPIResponse(
            success=False,
            error_code=error.get("code"),
            error_subcode=error.get("error_subcode"),
            error_message=error.get("message"),
            error_type=error.get("type"),
        )

    return GraphAPIResponse(success=True, data=body)
