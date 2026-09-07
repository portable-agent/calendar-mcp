import time
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from portable_agent_calendar.config.oidc_token_verifier import OidcTokenVerifier


@pytest.mark.anyio
async def test_verify_token_when_claims_are_valid_should_return_access_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verifier = OidcTokenVerifier(
        issuer="http://localhost:8081/realms/portable-agent",
        jwks_url="http://localhost:8081/realms/portable-agent/protocol/openid-connect/certs",
        audience="calendar-mcp",
    )
    monkeypatch.setattr(verifier, "_read_claims", lambda _token: valid_claims())

    result = await verifier.verify_token("signed-token")

    assert result is not None
    assert result.client_id == "mcp-gateway"
    assert result.subject == "user-1"
    assert result.scopes == ["calendar:write", "profile"]
    assert result.claims is not None
    assert result.claims["tenant_id"] == "81410813-f15f-4204-b9f5-53c30f465ffc"


@pytest.mark.anyio
async def test_verify_token_when_signature_is_invalid_should_reject_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verifier = OidcTokenVerifier(
        issuer="http://localhost:8081/realms/portable-agent",
        jwks_url="http://localhost:8081/realms/portable-agent/protocol/openid-connect/certs",
        audience="calendar-mcp",
    )

    def reject(_token: str) -> dict[str, Any]:
        raise jwt.InvalidTokenError("bad signature")

    monkeypatch.setattr(verifier, "_read_claims", reject)

    assert await verifier.verify_token("bad-token") is None


def valid_claims() -> dict[str, Any]:
    return {
        "sub": "user-1",
        "azp": "mcp-gateway",
        "scope": "calendar:write profile",
        "exp": 2_000_000_000,
        "tenant_id": "81410813-f15f-4204-b9f5-53c30f465ffc",
    }


@pytest.mark.anyio
async def test_verify_token_when_jwt_is_signed_should_check_standard_claims(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    issuer = "http://localhost:8081/realms/portable-agent"
    claims = {
        **valid_claims(),
        "iss": issuer,
        "aud": "calendar-mcp",
        "iat": int(time.time()),
    }
    signed_token = jwt.encode(claims, private_key, algorithm="RS256")
    verifier = OidcTokenVerifier(
        issuer=issuer,
        jwks_url=f"{issuer}/protocol/openid-connect/certs",
        audience="calendar-mcp",
    )

    class SigningKey:
        key = private_key.public_key()

    monkeypatch.setattr(
        verifier._key_client,
        "get_signing_key_from_jwt",
        lambda _token: SigningKey(),
    )

    assert await verifier.verify_token(signed_token) is not None
