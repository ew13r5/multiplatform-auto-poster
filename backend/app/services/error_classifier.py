from dataclasses import dataclass
from typing import Optional


@dataclass
class GraphAPIError:
    """Structured error from Graph API with retry guidance."""
    code: int
    subcode: Optional[int]
    message: str
    error_type: str           # rate_limit, auth, content_policy, duplicate, network, other
    is_retriable: bool
    retry_delay_seconds: int  # 0 if not retriable


# Rate limit error codes
_RATE_LIMIT_CODES = {4, 17, 32}


def classify_error(code: int, subcode: Optional[int], message: str) -> GraphAPIError:
    """Classify a Graph API error response into a structured error with retry guidance."""
    if code in _RATE_LIMIT_CODES:
        return GraphAPIError(
            code=code, subcode=subcode, message=message,
            error_type="rate_limit", is_retriable=True, retry_delay_seconds=300,
        )
    if code == 190:
        return GraphAPIError(
            code=code, subcode=subcode, message=message,
            error_type="auth", is_retriable=False, retry_delay_seconds=0,
        )
    if code == 368:
        return GraphAPIError(
            code=code, subcode=subcode, message=message,
            error_type="content_policy", is_retriable=False, retry_delay_seconds=0,
        )
    if code == 506:
        return GraphAPIError(
            code=code, subcode=subcode, message=message,
            error_type="duplicate", is_retriable=False, retry_delay_seconds=0,
        )
    return GraphAPIError(
        code=code, subcode=subcode, message=message,
        error_type="other", is_retriable=False, retry_delay_seconds=0,
    )


def classify_network_error(exc: Exception) -> GraphAPIError:
    """Classify a network-level exception as a retriable error."""
    return GraphAPIError(
        code=0, subcode=None, message=str(exc),
        error_type="network", is_retriable=True, retry_delay_seconds=120,
    )
