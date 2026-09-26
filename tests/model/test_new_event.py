from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime

import pytest

from portable_agent_calendar.model.new_event import NewEvent
from tests.factories import event_data


def test_create_when_end_is_after_start_should_keep_values() -> None:
    event = event_data()

    assert event.title == "Обсуждение проекта"
    assert event.start_time == datetime(2026, 9, 8, 9, 0, tzinfo=UTC)
    assert event.end_time == datetime(2026, 9, 8, 9, 30, tzinfo=UTC)


def test_create_when_end_is_not_after_start_should_reject_event() -> None:
    with pytest.raises(ValueError, match="endAt"):
        NewEvent.from_text(
            tenant_id="81410813-f15f-4204-b9f5-53c30f465ffc",
            request_key="request-123",
            title="Demo",
            start_at="2026-09-08T12:30:00+03:00",
            end_at="2026-09-08T12:00:00+03:00",
            time_zone="Europe/Moscow",
        )


def test_create_when_time_zone_is_unknown_should_reject_event() -> None:
    with pytest.raises(ValueError, match="timeZone"):
        NewEvent.from_text(
            tenant_id="81410813-f15f-4204-b9f5-53c30f465ffc",
            request_key="request-123",
            title="Demo",
            start_at="2026-09-08T12:00:00+03:00",
            end_at="2026-09-08T12:30:00+03:00",
            time_zone="Mars/Olympus",
        )


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda event: replace(event, title=" "), "title"),
        (lambda event: replace(event, request_key=""), "requestKey"),
        (lambda event: replace(event, description="a" * 2001), "description"),
        (
            lambda event: replace(event, attendees=("person@example.test", "person@example.test")),
            "unique",
        ),
        (lambda event: replace(event, attendees=("not-an-email",)), "email"),
    ],
)
def test_create_when_field_is_invalid_should_reject_event(
    change: Callable[[NewEvent], NewEvent], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        change(event_data())


def test_create_when_tenant_is_not_uuid_should_reject_event() -> None:
    with pytest.raises(ValueError):
        replace(event_data(), tenant_id="not-a-uuid")


def test_create_when_tenant_uuid_has_other_form_should_normalize_it() -> None:
    event = replace(event_data(), tenant_id="81410813F15F4204B9F553C30F465FFC")

    assert event.tenant_id == "81410813-f15f-4204-b9f5-53c30f465ffc"


def test_create_when_actor_uuid_has_other_form_should_normalize_it() -> None:
    event = replace(event_data(), actor_id="28EFC74EE82B4EA291434DC24C13FE0D")

    assert event.actor_id == "28efc74e-e82b-4ea2-9143-4dc24c13fe0d"


def test_create_when_actor_is_not_uuid_should_reject_event() -> None:
    with pytest.raises(ValueError):
        replace(event_data(), actor_id="not-a-uuid")


def test_create_when_time_has_no_offset_should_reject_event() -> None:
    with pytest.raises(ValueError, match="offset"):
        replace(event_data(), start_at="2026-09-08T12:00:00")


def test_create_when_time_is_not_iso_should_reject_event() -> None:
    with pytest.raises(ValueError, match="startAt"):
        replace(event_data(), start_at="tomorrow")
