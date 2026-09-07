from uuid import UUID

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.mcpserver.exceptions import ToolError


def current_tenant() -> str:
    token = get_access_token()
    value = token.claims.get("tenant_id") if token is not None and token.claims else None
    if not isinstance(value, str):
        raise ToolError("Authenticated tenant is missing")
    try:
        return str(UUID(value))
    except ValueError as error:
        raise ToolError("Authenticated tenant is invalid") from error
