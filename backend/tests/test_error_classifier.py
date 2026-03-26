import httpx
from app.services.error_classifier import classify_error, classify_network_error


def test_code_4_rate_limit():
    err = classify_error(4, None, "App request limit")
    assert err.error_type == "rate_limit"
    assert err.is_retriable is True
    assert err.retry_delay_seconds == 300


def test_code_17_rate_limit():
    err = classify_error(17, None, "User limit")
    assert err.error_type == "rate_limit"
    assert err.is_retriable is True


def test_code_32_rate_limit():
    err = classify_error(32, None, "Page limit")
    assert err.error_type == "rate_limit"
    assert err.is_retriable is True


def test_code_190_auth():
    err = classify_error(190, None, "Invalid token")
    assert err.error_type == "auth"
    assert err.is_retriable is False
    assert err.retry_delay_seconds == 0


def test_code_190_subcode_463():
    err = classify_error(190, 463, "Token expired")
    assert err.error_type == "auth"
    assert err.code == 190
    assert err.subcode == 463


def test_code_368_content_policy():
    err = classify_error(368, None, "Content blocked")
    assert err.error_type == "content_policy"
    assert err.is_retriable is False


def test_code_506_duplicate():
    err = classify_error(506, None, "Duplicate")
    assert err.error_type == "duplicate"
    assert err.is_retriable is False


def test_network_error():
    err = classify_network_error(httpx.TimeoutException("timeout"))
    assert err.error_type == "network"
    assert err.is_retriable is True
    assert err.retry_delay_seconds == 120


def test_connect_error():
    err = classify_network_error(httpx.ConnectError("refused"))
    assert err.error_type == "network"
    assert err.is_retriable is True


def test_unknown_code():
    err = classify_error(9999, None, "Unknown")
    assert err.error_type == "other"
    assert err.is_retriable is False
