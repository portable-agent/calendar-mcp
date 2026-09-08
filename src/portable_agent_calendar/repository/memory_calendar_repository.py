from threading import Lock

from portable_agent_calendar.model.calendar_event import CalendarEvent


class MemoryCalendarRepository:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], CalendarEvent] = {}
        self._lock = Lock()

    async def find(self, tenant_id: str, request_key: str) -> CalendarEvent | None:
        with self._lock:
            return self._events.get((tenant_id, request_key))

    async def save_if_missing(self, event: CalendarEvent) -> CalendarEvent:
        key = (event.data.tenant_id, event.data.request_key)
        with self._lock:
            return self._events.setdefault(key, event)

    async def find_by_request_key(self, request_key: str) -> list[CalendarEvent]:
        with self._lock:
            return [event for (_, key), event in self._events.items() if key == request_key]
