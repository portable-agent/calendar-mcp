from collections.abc import Callable

from mcp.server import MCPServer
from mcp.server.auth.provider import TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel, ConfigDict, Field

from portable_agent_calendar.model.new_event import NewEvent
from portable_agent_calendar.service.calendar_service import CalendarService


class EventResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    event_id: str = Field(alias="eventId")


def build_server(
    service: CalendarService,
    *,
    current_tenant: Callable[[], str],
    auth: AuthSettings | None = None,
    token_verifier: TokenVerifier | None = None,
) -> MCPServer:
    server = MCPServer(
        name="calendar-mcp",
        title="Portable Agent Calendar",
        description="Создаёт события через выбранный календарный коннектор.",
        version="0.1.0",
        auth=auth,
        token_verifier=token_verifier,
    )

    @server.tool(
        name="create_event",
        description="Создать событие календаря. Повторный request_key не создаёт дубликат.",
        annotations=ToolAnnotations(
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=True,
        ),
    )
    async def create_event(
        request_key: str,
        title: str,
        start_at: str,
        end_at: str,
        time_zone: str,
        actor_id: str | None = None,
        description: str | None = None,
        attendees: list[str] | None = None,
    ) -> EventResult:
        try:
            event = await service.create(
                NewEvent.from_text(
                    tenant_id=current_tenant(),
                    request_key=request_key,
                    title=title,
                    start_at=start_at,
                    end_at=end_at,
                    time_zone=time_zone,
                    actor_id=actor_id,
                    description=description,
                    attendees=attendees,
                )
            )
        except ValueError as error:
            raise ToolError(str(error)) from error
        return EventResult(eventId=event.event_id)

    return server
