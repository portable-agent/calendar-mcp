from collections.abc import Callable

import httpx

from portable_agent_calendar.client.connection_token_client import HttpConnectionTokenClient
from portable_agent_calendar.config.settings import Settings
from portable_agent_calendar.provider.calendar_provider import CalendarProvider
from portable_agent_calendar.provider.fake_calendar import FakeCalendar
from portable_agent_calendar.provider.google_calendar import GoogleCalendar
from portable_agent_calendar.repository.calendar_repository import CalendarRepository


def build_provider(settings: Settings, repository: CalendarRepository) -> CalendarProvider:
    timeout = httpx.Timeout(
        settings.remote_read_timeout,
        connect=settings.remote_connect_timeout,
    )
    providers: dict[str, Callable[[], CalendarProvider]] = {
        "fake-calendar": lambda: FakeCalendar(repository),
        "google-calendar": lambda: GoogleCalendar(
            HttpConnectionTokenClient(str(settings.connection_url), timeout=timeout),
            str(settings.google_api_url),
            timeout=timeout,
        ),
    }
    return providers[settings.provider]()
