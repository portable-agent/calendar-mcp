from dataclasses import dataclass

from portable_agent_calendar.model.new_event import NewEvent


@dataclass(frozen=True, slots=True)
class CalendarEvent:
    event_id: str
    data: NewEvent
