import json
from dataclasses import replace
from unittest.mock import AsyncMock

import httpx
import pytest

from portable_agent_calendar.provider.google_calendar import GoogleCalendar
from tests.factories import event_data

ACTOR_ID = "28efc74e-e82b-4ea2-9143-4dc24c13fe0d"


@pytest.mark.anyio
async def test_create_should_get_user_token_and_send_google_event() -> None:
    requests: list[httpx.Request] = []

    async def answer(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"id": "google-event-id"})

    token_client = AsyncMock()
    token_client.get.return_value = "google-access-token"
    provider = GoogleCalendar(
        token_client,
        "https://www.googleapis.com/calendar/v3",
        transport=httpx.MockTransport(answer),
    )
    data = replace(event_data(), actor_id=ACTOR_ID)

    event = await provider.create(data, "service-token")

    assert event.event_id == "google-event-id"
    token_client.get.assert_awaited_once_with(ACTOR_ID, "service-token")
    request = requests[0]
    assert request.method == "POST"
    assert request.url.path == "/calendar/v3/calendars/primary/events"
    assert request.headers["Authorization"] == "Bearer google-access-token"
    body = json.loads(request.content)
    assert body["summary"] == "Обсуждение проекта"
    assert body["start"] == {
        "dateTime": "2026-09-08T12:00:00+03:00",
        "timeZone": "Europe/Moscow",
    }
    assert body["end"] == {
        "dateTime": "2026-09-08T12:30:00+03:00",
        "timeZone": "Europe/Moscow",
    }
    assert set(body["id"]) <= set("0123456789abcdefghijklmnopqrstuv")
    assert 5 <= len(body["id"]) <= 1024


@pytest.mark.anyio
async def test_create_when_event_exists_should_return_same_event() -> None:
    paths: list[str] = []

    async def answer(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        if request.method == "POST":
            return httpx.Response(409)
        return httpx.Response(200, json={"id": request.url.path.rsplit("/", 1)[-1]})

    token_client = AsyncMock()
    token_client.get.return_value = "google-access-token"
    provider = GoogleCalendar(
        token_client,
        "https://www.googleapis.com/calendar/v3",
        transport=httpx.MockTransport(answer),
    )

    event = await provider.create(replace(event_data(), actor_id=ACTOR_ID), "service-token")

    assert event.event_id
    assert paths == [
        "/calendar/v3/calendars/primary/events",
        f"/calendar/v3/calendars/primary/events/{event.event_id}",
    ]


@pytest.mark.anyio
async def test_create_when_actor_is_missing_should_reject_request() -> None:
    provider = GoogleCalendar(AsyncMock(), "https://www.googleapis.com/calendar/v3")

    with pytest.raises(ValueError, match="actorId is required for Google Calendar"):
        await provider.create(event_data(), "service-token")
