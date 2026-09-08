import asyncio
from typing import Any
from uuid import UUID

import jwt
from mcp.server.auth.provider import AccessToken


class OidcTokenVerifier:
    def __init__(self, *, issuer: str, jwks_url: str, audience: str) -> None:
        self._issuer = issuer.rstrip("/")
        self._audience = audience
        self._key_client = jwt.PyJWKClient(jwks_url)

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            claims = await asyncio.to_thread(self._read_claims, token)
            tenant_id = str(UUID(self._text_claim(claims, "tenant_id")))
            subject = self._text_claim(claims, "sub")
            client_id = self._client_id(claims)
            expires_at = int(claims["exp"])
            scopes = self._scopes(claims)
        except jwt.PyJWTError, KeyError, TypeError, ValueError:
            return None

        safe_claims = dict(claims)
        safe_claims["tenant_id"] = tenant_id
        return AccessToken(
            token=token,
            client_id=client_id,
            scopes=scopes,
            expires_at=expires_at,
            resource=self._audience,
            subject=subject,
            claims=safe_claims,
        )

    def _read_claims(self, token: str) -> dict[str, Any]:
        key = self._key_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            audience=self._audience,
            issuer=self._issuer,
            options={"require": ["exp", "iat", "iss", "sub", "aud", "tenant_id"]},
        )
        return claims

    @staticmethod
    def _text_claim(claims: dict[str, Any], name: str) -> str:
        value = claims[name]
        if not isinstance(value, str) or not value:
            raise ValueError(f"{name} must be a non-empty string")
        return value

    @classmethod
    def _client_id(cls, claims: dict[str, Any]) -> str:
        value = claims.get("azp", claims.get("client_id"))
        if not isinstance(value, str) or not value:
            raise ValueError("azp or client_id must be a non-empty string")
        return value

    @staticmethod
    def _scopes(claims: dict[str, Any]) -> list[str]:
        value = claims.get("scope", "")
        if not isinstance(value, str):
            raise ValueError("scope must be a string")
        return value.split()
