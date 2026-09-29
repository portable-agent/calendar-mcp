from typing import Any, Protocol

import httpx


class ConnectionTokenClient(Protocol):
    async def get(self, actor_id: str, service_token: str) -> str: ...


class ConnectionRequiredError(ValueError):
    pass


class ConnectionAmbiguousError(ValueError):
    pass


class ConnectionCallError(ValueError):
    pass


class HttpConnectionTokenClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: httpx.Timeout | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url
        self._timeout = timeout or httpx.Timeout(10.0, connect=3.0)
        self._transport = transport

    async def get(self, actor_id: str, service_token: str) -> str:
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    "/internal/v1/tokens",
                    headers={"Authorization": f"Bearer {service_token}"},
                    json={"actorId": actor_id, "provider": "google-calendar"},
                )
        except httpx.HTTPError as error:
            raise ConnectionCallError("Connection Service is unavailable") from error

        if response.status_code == 409:
            self._raise_conflict(response)
        if response.is_error:
            raise ConnectionCallError("Connection Service rejected token request")

        token = self._json(response).get("accessToken")
        if not isinstance(token, str) or not token:
            raise ConnectionCallError("Connection Service returned invalid token response")
        return token

    @staticmethod
    def _raise_conflict(response: httpx.Response) -> None:
        problem_type = HttpConnectionTokenClient._json(response).get("type")
        if problem_type == "https://portable-agent.dev/problems/connection-required":
            raise ConnectionRequiredError("Google Calendar connection is required")
        if problem_type == "https://portable-agent.dev/problems/connection-ambiguous":
            raise ConnectionAmbiguousError("Google Calendar connection choice is required")
        raise ConnectionCallError("Connection Service returned unknown conflict")

    @staticmethod
    def _json(response: httpx.Response) -> dict[str, Any]:
        try:
            value: object = response.json()
        except ValueError as error:
            raise ConnectionCallError("Connection Service returned invalid response") from error
        if not isinstance(value, dict):
            raise ConnectionCallError("Connection Service returned invalid response")
        return value
