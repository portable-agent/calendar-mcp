import json

import httpx
import pytest

from portable_agent_calendar.client.connection_token_client import (
    ConnectionRequiredError,
    HttpConnectionTokenClient,
)


@pytest.mark.anyio
async def test_get_should_forward_service_token_and_return_google_token() -> None:
    async def answer(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/internal/v1/tokens"
        assert request.headers["Authorization"] == "Bearer service-token"
        assert json.loads(request.content) == {
            "actorId": "28efc74e-e82b-4ea2-9143-4dc24c13fe0d",
            "provider": "google-calendar",
        }
        return httpx.Response(
            200,
            json={
                "accessToken": "google-access-token",
                "tokenType": "Bearer",
                "expiresAt": "2026-09-29T16:00:00Z",
            },
        )

    client = HttpConnectionTokenClient(
        "http://connection-service:8080",
        transport=httpx.MockTransport(answer),
    )

    token = await client.get(
        "28efc74e-e82b-4ea2-9143-4dc24c13fe0d",
        "service-token",
    )

    assert token == "google-access-token"


@pytest.mark.anyio
async def test_get_when_connection_is_missing_should_return_safe_error() -> None:
    async def answer(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            409,
            json={
                "type": "https://portable-agent.dev/problems/connection-required",
                "title": "Connection is required",
                "status": 409,
            },
        )

    client = HttpConnectionTokenClient(
        "http://connection-service:8080",
        transport=httpx.MockTransport(answer),
    )

    with pytest.raises(ConnectionRequiredError, match="Google Calendar connection is required"):
        await client.get(
            "28efc74e-e82b-4ea2-9143-4dc24c13fe0d",
            "service-token",
        )
