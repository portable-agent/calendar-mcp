import secrets
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings

from portable_agent_calendar.controller.calendar_mcp import build_server
from portable_agent_calendar.controller.current_tenant import current_service_token, current_tenant
from portable_agent_calendar.model.calendar_event import CalendarEvent
from portable_agent_calendar.repository.calendar_repository import CalendarRepository
from portable_agent_calendar.service.calendar_service import CalendarService


def build_app(
    service: CalendarService,
    repository: CalendarRepository,
    *,
    test_api_enabled: bool,
    test_api_key: str | None = None,
    auth: AuthSettings | None = None,
    token_verifier: TokenVerifier | None = None,
    allowed_hosts: list[str] | None = None,
    allowed_origins: list[str] | None = None,
) -> FastAPI:
    security = TransportSecuritySettings(
        allowed_hosts=allowed_hosts
        if allowed_hosts is not None
        else ["127.0.0.1:*", "localhost:*", "[::1]:*"],
        allowed_origins=allowed_origins
        if allowed_origins is not None
        else ["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"],
    )
    mcp_app = build_server(
        service,
        current_tenant=current_tenant,
        current_token=current_service_token,
        auth=auth,
        token_verifier=token_verifier,
    ).streamable_http_app(
        json_response=True,
        stateless_http=True,
        streamable_http_path="/mcp",
        transport_security=security,
    )
    app = FastAPI(
        title="Calendar MCP",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=mcp_app.router.lifespan_context,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "UP"}

    if test_api_enabled:

        @app.get("/test/events")
        async def find_events(
            request_key: str = Query(alias="requestKey", min_length=1, max_length=128),
            given_key: str | None = Header(default=None, alias="X-Test-Key"),
        ) -> dict[str, list[dict[str, Any]]]:
            if (
                test_api_key is None
                or given_key is None
                or not secrets.compare_digest(given_key, test_api_key)
            ):
                raise HTTPException(status_code=401, detail="Invalid test key")
            events = await repository.find_by_request_key(request_key)
            return {"events": [_event_json(event) for event in events]}

    app.mount("/", mcp_app)
    return app


def _event_json(event: CalendarEvent) -> dict[str, Any]:
    data = event.data
    return {
        "eventId": event.event_id,
        "tenantId": data.tenant_id,
        "requestKey": data.request_key,
        "title": data.title,
        "startAt": data.start_at,
        "endAt": data.end_at,
        "timeZone": data.time_zone,
        "description": data.description,
        "attendees": list(data.attendees),
    }
