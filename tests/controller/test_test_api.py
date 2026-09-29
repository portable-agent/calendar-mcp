import asyncio

from fastapi.testclient import TestClient
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl

from portable_agent_calendar.controller.app import build_app
from portable_agent_calendar.provider.fake_calendar import FakeCalendar
from portable_agent_calendar.repository.memory_calendar_repository import MemoryCalendarRepository
from portable_agent_calendar.service.calendar_service import CalendarService
from tests.factories import event_data


class AcceptTokenVerifier:
    async def verify_token(self, token: str) -> AccessToken | None:
        if token != "valid-token":
            return None
        return AccessToken(
            token=token,
            client_id="mcp-gateway",
            scopes=["calendar:write"],
            subject="user-1",
            claims={"tenant_id": "81410813-f15f-4204-b9f5-53c30f465ffc"},
        )


def test_find_events_when_test_api_is_enabled_should_return_camel_case_data() -> None:
    repository = MemoryCalendarRepository()
    service = CalendarService(FakeCalendar(repository))
    app = build_app(
        service,
        repository,
        test_api_enabled=True,
        test_api_key="local-test-key",
    )
    event_id = asyncio.run(service.create(event_data())).event_id

    with TestClient(app) as client:
        health = client.get("/health")
        response = client.get(
            "/test/events",
            params={"requestKey": "request-123"},
            headers={"X-Test-Key": "local-test-key"},
        )

    assert health.json() == {"status": "UP"}
    assert response.status_code == 200
    assert response.json() == {
        "events": [
            {
                "eventId": event_id,
                "tenantId": "81410813-f15f-4204-b9f5-53c30f465ffc",
                "requestKey": "request-123",
                "title": "Обсуждение проекта",
                "startAt": "2026-09-08T12:00:00+03:00",
                "endAt": "2026-09-08T12:30:00+03:00",
                "timeZone": "Europe/Moscow",
                "description": None,
                "attendees": [],
            }
        ]
    }


def test_find_events_when_test_api_is_disabled_should_return_not_found() -> None:
    repository = MemoryCalendarRepository()
    app = build_app(CalendarService(FakeCalendar(repository)), repository, test_api_enabled=False)

    with TestClient(app) as client:
        response = client.get("/test/events", params={"requestKey": "request-123"})

    assert response.status_code == 404


def test_find_events_when_test_key_is_wrong_should_reject_request() -> None:
    repository = MemoryCalendarRepository()
    app = build_app(
        CalendarService(FakeCalendar(repository)),
        repository,
        test_api_enabled=True,
        test_api_key="local-test-key",
    )

    with TestClient(app) as client:
        response = client.get(
            "/test/events",
            params={"requestKey": "request-123"},
            headers={"X-Test-Key": "wrong-key"},
        )

    assert response.status_code == 401


def test_find_events_when_test_key_is_missing_should_reject_request() -> None:
    repository = MemoryCalendarRepository()
    app = build_app(
        CalendarService(FakeCalendar(repository)),
        repository,
        test_api_enabled=True,
        test_api_key="local-test-key",
    )

    with TestClient(app) as client:
        response = client.get("/test/events", params={"requestKey": "request-123"})

    assert response.status_code == 401


def test_mcp_when_host_is_not_allowed_should_reject_request() -> None:
    repository = MemoryCalendarRepository()
    app = build_app(CalendarService(FakeCalendar(repository)), repository, test_api_enabled=False)

    with TestClient(app) as client:
        response = client.post("/mcp", headers={"host": "evil.example"}, json={})

    assert response.status_code == 421


def test_mcp_when_token_is_valid_should_use_tenant_from_token() -> None:
    repository = MemoryCalendarRepository()
    app = build_app(
        CalendarService(FakeCalendar(repository)),
        repository,
        test_api_enabled=False,
        auth=AuthSettings(
            issuer_url=AnyHttpUrl("http://localhost:8081/realms/portable-agent"),
            resource_server_url=AnyHttpUrl("http://localhost:8080/mcp"),
            required_scopes=["calendar:write"],
        ),
        token_verifier=AcceptTokenVerifier(),
    )

    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            headers={
                "Authorization": "Bearer valid-token",
                "Accept": "application/json, text/event-stream",
                "Host": "localhost:8080",
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "create_event",
                    "arguments": {
                        "request_key": "auth-request",
                        "title": "Auth test",
                        "start_at": "2026-09-08T12:00:00+03:00",
                        "end_at": "2026-09-08T12:30:00+03:00",
                        "time_zone": "Europe/Moscow",
                    },
                },
            },
        )

    assert response.status_code == 200
    assert response.json()["result"]["structuredContent"]["eventId"]
