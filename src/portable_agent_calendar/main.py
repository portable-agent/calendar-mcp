from mcp.server.auth.settings import AuthSettings

from portable_agent_calendar.config.oidc_token_verifier import OidcTokenVerifier
from portable_agent_calendar.config.settings import Settings
from portable_agent_calendar.controller.app import build_app
from portable_agent_calendar.repository.memory_calendar_repository import MemoryCalendarRepository
from portable_agent_calendar.service.calendar_service import CalendarService

repository = MemoryCalendarRepository()
service = CalendarService(repository)
settings = Settings()
token_verifier = OidcTokenVerifier(
    issuer=str(settings.oidc_issuer_url),
    jwks_url=str(settings.oidc_jwks_url),
    audience=settings.oidc_audience,
)
auth = AuthSettings(
    issuer_url=settings.oidc_issuer_url,
    resource_server_url=settings.mcp_resource_url,
    required_scopes=settings.mcp_required_scopes,
)
app = build_app(
    service,
    repository,
    test_api_enabled=settings.test_api_enabled,
    test_api_key=settings.test_api_key,
    auth=auth,
    token_verifier=token_verifier,
    allowed_hosts=settings.mcp_allowed_hosts,
    allowed_origins=settings.mcp_allowed_origins,
)
