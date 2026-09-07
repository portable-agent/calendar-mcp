from fastapi import FastAPI
from fastapi.testclient import TestClient

from portable_agent_calendar.main import app


def test_main_should_build_fastapi_app() -> None:
    assert isinstance(app, FastAPI)


def test_main_when_mcp_has_no_token_should_require_authentication() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            headers={"host": "localhost:8080", "accept": "application/json, text/event-stream"},
            json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        )

    assert response.status_code == 401
