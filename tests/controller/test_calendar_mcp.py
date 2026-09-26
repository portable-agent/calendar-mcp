import pytest
from mcp import Client
from mcp.types import TextContent

from portable_agent_calendar.controller.calendar_mcp import build_server
from portable_agent_calendar.repository.memory_calendar_repository import MemoryCalendarRepository
from portable_agent_calendar.service.calendar_service import CalendarService


@pytest.mark.anyio
async def test_create_event_when_input_is_valid_should_return_event_id() -> None:
    repository = MemoryCalendarRepository()
    server = build_server(
        CalendarService(repository),
        current_tenant=lambda: "81410813-f15f-4204-b9f5-53c30f465ffc",
    )

    async with Client(server, raise_exceptions=True) as client:
        result = await client.call_tool(
            "create_event",
            {
                "request_key": "request-123",
                "title": "Обсуждение проекта",
                "start_at": "2026-09-08T12:00:00+03:00",
                "end_at": "2026-09-08T12:30:00+03:00",
                "time_zone": "Europe/Moscow",
                "actor_id": "28efc74e-e82b-4ea2-9143-4dc24c13fe0d",
            },
        )

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["eventId"]
    events = await repository.find_by_request_key("request-123")
    assert events[0].data.actor_id == "28efc74e-e82b-4ea2-9143-4dc24c13fe0d"


@pytest.mark.anyio
async def test_list_tools_should_publish_only_create_event() -> None:
    server = build_server(
        CalendarService(MemoryCalendarRepository()),
        current_tenant=lambda: "81410813-f15f-4204-b9f5-53c30f465ffc",
    )

    async with Client(server, raise_exceptions=True) as client:
        tools = await client.list_tools()

    assert [tool.name for tool in tools.tools] == ["create_event"]
    tool = tools.tools[0]
    assert tool.input_schema["required"] == [
        "request_key",
        "title",
        "start_at",
        "end_at",
        "time_zone",
    ]
    assert "actor_id" in tool.input_schema["properties"]
    assert tool.annotations is not None
    assert tool.annotations.idempotent_hint is True
    assert tool.annotations.read_only_hint is False


@pytest.mark.anyio
async def test_create_event_when_time_is_invalid_should_return_safe_error() -> None:
    server = build_server(
        CalendarService(MemoryCalendarRepository()),
        current_tenant=lambda: "81410813-f15f-4204-b9f5-53c30f465ffc",
    )

    async with Client(server, raise_exceptions=True) as client:
        result = await client.call_tool(
            "create_event",
            {
                "request_key": "request-123",
                "title": "Demo",
                "start_at": "2026-09-08T12:30:00+03:00",
                "end_at": "2026-09-08T12:00:00+03:00",
                "time_zone": "Europe/Moscow",
            },
        )

    assert result.is_error is True
    assert isinstance(result.content[0], TextContent)
    assert "endAt" in result.content[0].text
