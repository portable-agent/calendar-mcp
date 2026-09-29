from uuid import uuid4

from portable_agent_calendar.model.calendar_event import CalendarEvent
from portable_agent_calendar.model.errors import RequestKeyConflictError
from portable_agent_calendar.model.new_event import NewEvent
from portable_agent_calendar.repository.calendar_repository import CalendarRepository


class FakeCalendar:
    def __init__(self, repository: CalendarRepository) -> None:
        self._repository = repository

    async def create(self, data: NewEvent) -> CalendarEvent:
        old_event = await self._repository.find(data.tenant_id, data.request_key)
        if old_event is not None:
            return self._same_event(old_event, data)

        new_event = CalendarEvent(event_id=str(uuid4()), data=data)
        saved_event = await self._repository.save_if_missing(new_event)
        return self._same_event(saved_event, data)

    @staticmethod
    def _same_event(saved: CalendarEvent, data: NewEvent) -> CalendarEvent:
        if saved.data != data:
            raise RequestKeyConflictError("requestKey is already used with other event data")
        return saved
