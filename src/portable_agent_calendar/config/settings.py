from typing import Literal

from pydantic import AnyHttpUrl, Field, PositiveFloat, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CALENDAR_", extra="ignore")

    test_api_enabled: bool = False
    test_api_key: str | None = None
    provider: Literal["fake-calendar", "google-calendar"] = "fake-calendar"
    connection_url: AnyHttpUrl = AnyHttpUrl("http://localhost:18088")
    google_api_url: AnyHttpUrl = AnyHttpUrl("https://www.googleapis.com/calendar/v3")
    remote_connect_timeout: PositiveFloat = 3.0
    remote_read_timeout: PositiveFloat = 10.0
    oidc_issuer_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8081/realms/portable-agent")
    oidc_jwks_url: AnyHttpUrl = AnyHttpUrl(
        "http://localhost:8081/realms/portable-agent/protocol/openid-connect/certs"
    )
    oidc_audience: str = "calendar-mcp"
    mcp_resource_url: AnyHttpUrl = AnyHttpUrl("http://localhost:18082/mcp")
    mcp_required_scopes: list[str] = Field(default_factory=lambda: ["calendar:write"])
    mcp_allowed_hosts: list[str] = Field(
        default_factory=lambda: ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    )
    mcp_allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:*",
            "http://localhost:*",
            "http://[::1]:*",
        ]
    )

    @model_validator(mode="after")
    def check_test_api_key(self) -> Settings:
        if self.test_api_enabled and not self.test_api_key:
            raise ValueError("CALENDAR_TEST_API_KEY is required when test API is enabled")
        return self
