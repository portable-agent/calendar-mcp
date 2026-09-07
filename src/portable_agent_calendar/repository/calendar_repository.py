from typing import Protocol

from portable_agent_calendar.model.calendar_event import CalendarEvent


class CalendarRepository(Protocol):
    async def find(self, tenant_id: str, request_key: str) -> CalendarEvent | None: ...

    async def save_if_missing(self, event: CalendarEvent) -> CalendarEvent: ...

    async def find_by_request_key(self, request_key: str) -> list[CalendarEvent]: ...
