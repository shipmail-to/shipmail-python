from unittest.mock import AsyncMock, patch

import httpx
import pytest

from shipmail import AsyncShipmail, Shipmail
from shipmail._base_client import RequestOptions, _parse_retry_after
from shipmail._errors import ShipmailError


@pytest.mark.parametrize("header", ["2", "Mon, 14 Sep 2026 12:00:02 GMT"])
def test_retry_after_seconds_and_date(header):
    with patch("shipmail._base_client.time.time", return_value=1789387200):
        assert _parse_retry_after(header) == 2


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("bytes_response", [False, True])
@pytest.mark.parametrize("method,key,header,expected", [
    ("GET", None, "2", 3),
    ("GET", None, "61", 1),
    ("POST", None, "0", 1),
    ("POST", "same-key", "0", 3),
    ("PATCH", "same-key", "0", 3),
    ("PUT", "same-key", "0", 3),
    ("DELETE", "same-key", "0", 1),
    ("POST", "   ", "0", 1),
    ("POST", "", "0", 1),
])
async def test_retry_policy(asynchronous, bytes_response, method, key, header, expected):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(503, text="busy", headers={"Retry-After": header})

    options = RequestOptions(method=method, path="/test", method_options={"idempotency_key": key})
    if asynchronous:
        async with AsyncShipmail("test", transport=httpx.MockTransport(handler)) as client:
            with patch("shipmail._client.asyncio.sleep", new_callable=AsyncMock) as sleep:
                with pytest.raises(ShipmailError):
                    await (client.request_bytes(options) if bytes_response else client.request(options))
    else:
        with Shipmail("test", transport=httpx.MockTransport(handler)) as client:
            with patch("shipmail._client.time.sleep") as sleep:
                with pytest.raises(ShipmailError):
                    (client.request_bytes(options) if bytes_response else client.request(options))
    assert len(requests) == expected
    assert sleep.call_count == expected - 1
    if expected > 1:
        assert all(call.args == (float(header),) for call in sleep.call_args_list)
    assert all(request.headers.get("idempotency-key") == (key or None) for request in requests)


@pytest.mark.parametrize("count", [-1, float("inf"), 1.5, True])
def test_invalid_retry_count(count):
    with pytest.raises(ValueError):
        Shipmail("test", max_retries=count)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method,key", [("POST", None), ("DELETE", "same-key")])
async def test_no_mutation_replay_after_network_failure(asynchronous, method, key):
    requests = []

    def handler(request):
        requests.append(request)
        raise httpx.ReadError("Connection lost after sending request")

    options = RequestOptions(method=method, path="/messages", method_options={"idempotency_key": key})
    if asynchronous:
        async with AsyncShipmail("test", transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(ShipmailError):
                await client.request(options)
    else:
        with Shipmail("test", transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(ShipmailError):
                client.request(options)
    assert len(requests) == 1
