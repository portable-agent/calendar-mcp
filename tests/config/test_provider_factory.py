from portable_agent_calendar.config.provider_factory import build_provider
from portable_agent_calendar.config.settings import Settings
from portable_agent_calendar.provider.fake_calendar import FakeCalendar
from portable_agent_calendar.provider.google_calendar import GoogleCalendar
from portable_agent_calendar.repository.memory_calendar_repository import MemoryCalendarRepository


def test_build_provider_when_fake_is_selected_should_return_fake_calendar() -> None:
    provider = build_provider(Settings(provider="fake-calendar"), MemoryCalendarRepository())

    assert isinstance(provider, FakeCalendar)


def test_build_provider_when_google_is_selected_should_return_google_calendar() -> None:
    provider = build_provider(Settings(provider="google-calendar"), MemoryCalendarRepository())

    assert isinstance(provider, GoogleCalendar)
