# Calendar MCP

MCP-сервис календаря для Portable Agent. Он принимает подтверждённую команду создания встречи,
проверяет данные и вызывает выбранный календарный коннектор. Сейчас реализован только безопасный
`fake-calendar`; Google, Outlook и другие провайдеры появятся отдельными адаптерами.

## Что уже работает

- официальный MCP Python SDK `2.0.0` и Streamable HTTP `/mcp`;
- MCP tool `create_event`;
- tenant из проверенного OIDC-токена и обязательный `request_key`;
- проверка подписи, issuer, audience, срока жизни и scope токена;
- атомарная защита от повторного создания встречи;
- проверка дат, часового пояса и ограничений контракта;
- закрытый по умолчанию test API `/test/events`;
- health check `/health`;
- unit, service, MCP и HTTP-тесты.

## Стек

Python 3.14, официальный MCP Python SDK, FastAPI, Pydantic, uv, pytest, Ruff, mypy и Docker.

## Быстрый запуск

```bash
uv sync --all-groups
uv run uvicorn portable_agent_calendar.main:app --reload --port 8080
```

Для локального acceptance-теста:

```powershell
$env:CALENDAR_TEST_API_ENABLED="true"
$env:CALENDAR_TEST_API_KEY="сгенерированный-локальный-секрет"
uv run uvicorn portable_agent_calendar.main:app --port 8080
```

Для Compose скопируй `.env.example` в локальный `.env` и замени пример случайным секретом. `.env` не
хранится в Git.

MCP endpoint: `http://localhost:8080/mcp`. Test API выключен, если переменная не задана.
MCP endpoint всегда требует OIDC Bearer token со scope `calendar:write` и audience `calendar-mcp`.
Для Docker/Kubernetes укажи JSON-массив разрешённых Host в `CALENDAR_MCP_ALLOWED_HOSTS` и адрес JWKS в
`CALENDAR_OIDC_JWKS_URL`.

Текущее memory-хранилище предназначено только для одного процесса и одной реплики. Не увеличивай
число Uvicorn workers или Kubernetes replicas до появления общего хранилища либо реального
календарного коннектора.

## Проверки

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv run mkdocs build --strict
```

## Где читать дальше

- `AGENTS.md` — короткая памятка для разработчика и агента;
- `docs/architecture.md` — слои и поток создания встречи;
- `docs/development.md` — TDD и локальная разработка;
- `docs/runbook.md` — запуск и диагностика.
