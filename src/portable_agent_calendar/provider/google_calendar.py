import base64
import hashlib
from typing import Any

import httpx

from portable_agent_calendar.client.connection_token_client import ConnectionTokenClient
from portable_agent_calendar.model.calendar_event import CalendarEvent
from portable_agent_calendar.model.new_event import NewEvent


class GoogleCalendar:
    def __init__(
        self,
        token_client: ConnectionTokenClient,
        base_url: str,
        *,
        timeout: httpx.Timeout | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._token_client = token_client
        self._base_url = base_url
        self._timeout = timeout or httpx.Timeout(10.0, connect=3.0)
        self._transport = transport

    async def create(self, data: NewEvent, service_token: str) -> CalendarEvent:
        if data.actor_id is None:
            raise ValueError("actorId is required for Google Calendar")

        access_token = await self._token_client.get(data.actor_id, service_token)
        event_id = self._event_id(data)
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    "/calendars/primary/events",
                    headers=headers,
                    json=self._body(data, event_id),
                )
                if response.status_code == 409:
                    response = await client.get(
                        f"/calendars/primary/events/{event_id}",
                        headers=headers,
                    )
        except httpx.HTTPError as error:
            raise ValueError("Google Calendar is unavailable") from error

        if response.is_error:
            raise ValueError("Google Calendar rejected event")
        response_id = self._json(response).get("id")
        if not isinstance(response_id, str) or not response_id:
            raise ValueError("Google Calendar returned invalid event")
        return CalendarEvent(event_id=response_id, data=data)

    @staticmethod
    def _event_id(data: NewEvent) -> str:
        source = f"{data.tenant_id}:{data.actor_id}:{data.request_key}".encode()
        digest = hashlib.sha256(source).digest()
        return base64.b32hexencode(digest).decode().lower().rstrip("=")

    @staticmethod
    def _body(data: NewEvent, event_id: str) -> dict[str, Any]:
        body: dict[str, Any] = {
            "id": event_id,
            "summary": data.title,
            "start": {"dateTime": data.start_at, "timeZone": data.time_zone},
            "end": {"dateTime": data.end_at, "timeZone": data.time_zone},
            "extendedProperties": {
                "private": {
                    "requestHash": hashlib.sha256(data.request_key.encode()).hexdigest(),
                }
            },
        }
        if data.description is not None:
            body["description"] = data.description
        if data.attendees:
            body["attendees"] = [{"email": email} for email in data.attendees]
        return body

    @staticmethod
    def _json(response: httpx.Response) -> dict[str, Any]:
        try:
            value: object = response.json()
        except ValueError as error:
            raise ValueError("Google Calendar returned invalid event") from error
        if not isinstance(value, dict):
            raise ValueError("Google Calendar returned invalid event")
        return value
