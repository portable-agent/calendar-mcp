from typing import Protocol

from portable_agent_calendar.model.calendar_event import CalendarEvent
from portable_agent_calendar.model.new_event import NewEvent


class CalendarProvider(Protocol):
    async def create(self, data: NewEvent, service_token: str) -> CalendarEvent: ...
