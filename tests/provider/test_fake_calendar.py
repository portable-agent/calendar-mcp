import asyncio

import pytest

from portable_agent_calendar.model.errors import RequestKeyConflictError
from portable_agent_calendar.provider.fake_calendar import FakeCalendar
from portable_agent_calendar.repository.memory_calendar_repository import MemoryCalendarRepository
from tests.factories import event_data


@pytest.mark.anyio
async def test_create_when_request_is_repeated_should_return_same_event() -> None:
    provider = FakeCalendar(MemoryCalendarRepository())

    first = await provider.create(event_data())
    second = await provider.create(event_data())

    assert second == first


@pytest.mark.anyio
async def test_create_when_requests_run_together_should_save_one_event() -> None:
    repository = MemoryCalendarRepository()
    provider = FakeCalendar(repository)

    first, second = await asyncio.gather(
        provider.create(event_data()), provider.create(event_data())
    )

    assert first == second
    assert len(await repository.find_by_request_key("request-123")) == 1


@pytest.mark.anyio
async def test_create_when_same_key_has_other_data_should_reject_request() -> None:
    provider = FakeCalendar(MemoryCalendarRepository())
    await provider.create(event_data())
    changed = event_data().with_title("Другая встреча")

    with pytest.raises(RequestKeyConflictError):
        await provider.create(changed)
