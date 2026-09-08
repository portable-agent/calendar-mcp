# Разработка

## Требования

- Python 3.14;
- uv;
- Git;
- Docker для проверки image.

## Запуск

```bash
uv sync --all-groups
uv run uvicorn portable_agent_calendar.main:app --reload --port 8080
```

MCP Inspector можно подключить к `http://localhost:8080/mcp`.

## TDD

1. Red — тест описывает поведение и падает.
2. Green — минимальный код делает тест зелёным.
3. Refactor — код упрощается без изменения поведения.

Большинство тестов проверяют model и service без сети. MCP-тест использует официальный `Client(server)`
в памяти. HTTP-тест проверяет только health и локальный test API.

## Проверки перед PR

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv run mkdocs build --strict
docker build -t calendar-mcp:local .
```
