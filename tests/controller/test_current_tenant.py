import pytest
from mcp.server.auth.middleware.auth_context import auth_context_var
from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
from mcp.server.auth.provider import AccessToken
from mcp.server.mcpserver.exceptions import ToolError

from portable_agent_calendar.controller.current_tenant import current_service_token, current_tenant


def test_current_tenant_when_token_has_claim_should_return_normalized_uuid() -> None:
    access_token = AccessToken(
        token="token",
        client_id="test-client",
        scopes=[],
        subject="user-1",
        claims={"tenant_id": "81410813F15F4204B9F553C30F465FFC"},
    )
    context_token = auth_context_var.set(AuthenticatedUser(access_token))
    try:
        assert current_tenant() == "81410813-f15f-4204-b9f5-53c30f465ffc"
    finally:
        auth_context_var.reset(context_token)


def test_current_tenant_when_token_is_missing_should_reject_call() -> None:
    with pytest.raises(ToolError, match="Authenticated tenant is missing"):
        current_tenant()


def test_current_tenant_when_claim_is_invalid_should_reject_call() -> None:
    access_token = AccessToken(
        token="token",
        client_id="test-client",
        scopes=[],
        claims={"tenant_id": "not-a-uuid"},
    )
    context_token = auth_context_var.set(AuthenticatedUser(access_token))
    try:
        with pytest.raises(ToolError, match="Authenticated tenant is invalid"):
            current_tenant()
    finally:
        auth_context_var.reset(context_token)


def test_current_service_token_should_return_raw_token() -> None:
    access_token = AccessToken(
        token="service-token",
        client_id="action-service",
        scopes=[],
        claims={"tenant_id": "81410813-f15f-4204-b9f5-53c30f465ffc"},
    )
    context_token = auth_context_var.set(AuthenticatedUser(access_token))
    try:
        assert current_service_token() == "service-token"
    finally:
        auth_context_var.reset(context_token)
