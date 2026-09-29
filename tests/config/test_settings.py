import pytest

from portable_agent_calendar.config.settings import Settings


def test_settings_when_env_is_missing_should_disable_test_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CALENDAR_TEST_API_ENABLED", raising=False)

    assert Settings().test_api_enabled is False


def test_settings_when_env_is_true_should_enable_test_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CALENDAR_TEST_API_ENABLED", "true")
    monkeypatch.setenv("CALENDAR_TEST_API_KEY", "local-test-key")

    assert Settings().test_api_enabled is True


def test_settings_when_test_api_has_no_key_should_reject_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CALENDAR_TEST_API_ENABLED", "true")
    monkeypatch.delenv("CALENDAR_TEST_API_KEY", raising=False)

    with pytest.raises(ValueError, match="CALENDAR_TEST_API_KEY"):
        Settings()


def test_settings_when_hosts_are_given_should_read_json_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CALENDAR_MCP_ALLOWED_HOSTS", '["calendar-mcp:*"]')

    assert Settings().mcp_allowed_hosts == ["calendar-mcp:*"]


def test_settings_when_provider_is_missing_should_use_fake_calendar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CALENDAR_PROVIDER", raising=False)

    assert Settings().provider == "fake-calendar"


def test_settings_when_provider_is_unknown_should_reject_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CALENDAR_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="provider"):
        Settings()
