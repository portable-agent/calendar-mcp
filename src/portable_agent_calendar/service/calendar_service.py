from portable_agent_calendar.model.calendar_event import CalendarEvent
from portable_agent_calendar.model.new_event import NewEvent
from portable_agent_calendar.provider.calendar_provider import CalendarProvider


class CalendarService:
    def __init__(self, provider: CalendarProvider) -> None:
        self._provider = provider

    async def create(self, data: NewEvent, service_token: str) -> CalendarEvent:
        return await self._provider.create(data, service_token)
