from unittest.mock import patch

import httpx
import pytest

from tricount_extractor.client.client import BACKOFF_BASE_SECONDS, TricountClient


AUTH_RESPONSE = httpx.Response(
    200,
    json={
        "Response": [
            {"Token": {"token": "tok"}},
            {"UserPerson": {"id": "uid"}},
        ]
    },
)
REGISTRY_RESPONSE = httpx.Response(200, json={"Response": []})


def _auth_only_handler(request):
    return AUTH_RESPONSE


def test_authenticate_recovers_after_transient_failures():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] < 3:
            raise httpx.ReadTimeout("boom")
        return AUTH_RESPONSE

    with patch("tricount_extractor.client.client.time.sleep") as sleep:
        with TricountClient(transport=httpx.MockTransport(handler)) as client:
            assert client._access_token.access_token == "tok"

    assert calls["n"] == 3
    assert [c.args[0] for c in sleep.call_args_list] == [
        BACKOFF_BASE_SECONDS,
        BACKOFF_BASE_SECONDS * 2,
    ]


def test_authenticate_raises_connection_error_after_max_retry():
    original = httpx.ConnectError("nope")
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        raise original

    max_retry = 3
    with patch("tricount_extractor.client.client.time.sleep") as sleep:
        with pytest.raises(ConnectionError) as exc_info:
            with TricountClient(
                transport=httpx.MockTransport(handler), max_retry=max_retry
            ):
                pass

    assert calls["n"] == max_retry
    assert sleep.call_count == max_retry - 1
    assert exc_info.value.__cause__ is original


def test_get_registry_recovers_after_transient_failures():
    registry_calls = {"n": 0}

    def handler(request):
        if "session-registry-installation" in str(request.url):
            return AUTH_RESPONSE
        registry_calls["n"] += 1
        if registry_calls["n"] < 2:
            raise httpx.ReadTimeout("boom")
        return REGISTRY_RESPONSE

    with patch("tricount_extractor.client.client.time.sleep") as sleep:
        with TricountClient(transport=httpx.MockTransport(handler)) as client:
            response = client.get_registry("reg-001")

    assert response.status_code == 200
    assert registry_calls["n"] == 2
    sleep.assert_called_once_with(BACKOFF_BASE_SECONDS)


def test_get_registry_raises_connection_error_after_max_retry():
    original = httpx.ReadTimeout("nope")
    registry_calls = {"n": 0}

    def handler(request):
        if "session-registry-installation" in str(request.url):
            return AUTH_RESPONSE
        registry_calls["n"] += 1
        raise original

    max_retry = 3
    with patch("tricount_extractor.client.client.time.sleep") as sleep:
        with TricountClient(
            transport=httpx.MockTransport(handler), max_retry=max_retry
        ) as client:
            with pytest.raises(ConnectionError) as exc_info:
                client.get_registry("reg-001")

    assert registry_calls["n"] == max_retry
    assert sleep.call_count == max_retry - 1
    assert exc_info.value.__cause__ is original


def test_get_registry_does_not_retry_on_http_error():
    calls = {"n": 0}

    def handler(request):
        if "session-registry-installation" in str(request.url):
            return AUTH_RESPONSE
        calls["n"] += 1
        return httpx.Response(404, json={"error": "not found"})

    with patch("tricount_extractor.client.client.time.sleep") as sleep:
        with TricountClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(httpx.HTTPStatusError):
                client.get_registry("reg-001")

    assert calls["n"] == 1
    sleep.assert_not_called()
