from portable_agent_calendar.model.new_event import NewEvent


def event_data() -> NewEvent:
    return NewEvent.from_text(
        tenant_id="81410813-f15f-4204-b9f5-53c30f465ffc",
        request_key="request-123",
        title="Обсуждение проекта",
        start_at="2026-09-08T12:00:00+03:00",
        end_at="2026-09-08T12:30:00+03:00",
        time_zone="Europe/Moscow",
    )
