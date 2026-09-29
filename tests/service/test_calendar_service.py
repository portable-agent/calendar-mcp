from unittest.mock import AsyncMock

import pytest

from portable_agent_calendar.model.calendar_event import CalendarEvent
from portable_agent_calendar.service.calendar_service import CalendarService
from tests.factories import event_data


@pytest.mark.anyio
async def test_create_should_use_selected_provider() -> None:
    data = event_data()
    expected = CalendarEvent(event_id="event-123", data=data)
    provider = AsyncMock()
    provider.create.return_value = expected
    service = CalendarService(provider)

    result = await service.create(data, "service-token")

    assert result == expected
    provider.create.assert_awaited_once_with(data, "service-token")
