# Calendar MCP

MCP-сервис календаря для Portable Agent. Он принимает подтверждённую команду создания встречи,
проверяет данные и вызывает выбранный календарный коннектор. Работают безопасный `fake-calendar` и
реальный `google-calendar`. Google access token приходит только через Connection Service и не
сохраняется в этом сервисе.

## Что уже работает

- официальный MCP Python SDK `2.0.0` и Streamable HTTP `/mcp`;
- MCP tool `create_event`;
- отдельная стратегия `FakeCalendar`, которую можно заменить без изменения use case;
- стратегия `GoogleCalendar` с детерминированным event ID и защитой от дублей;
- запрос короткоживущего Google access token у Connection Service;
- tenant из проверенного OIDC-токена и обязательный `request_key`;
- необязательный доверенный `actor_id` для выбора пользовательского подключения;
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

По умолчанию выбран `CALENDAR_PROVIDER=fake-calendar`. Для реального провайдера нужны только адреса,
не секреты:

```powershell
$env:CALENDAR_PROVIDER="google-calendar"
$env:CALENDAR_CONNECTION_URL="http://localhost:18088"
$env:CALENDAR_GOOGLE_API_URL="https://www.googleapis.com/calendar/v3"
```

Google provider требует доверенный `actor_id` и делегированный service token с audience
`connection-service` и scope `connection:token`. Refresh token остаётся внутри Connection Service.

MCP endpoint: `http://localhost:8080/mcp`. Test API выключен, если переменная не задана.
MCP endpoint всегда требует OIDC Bearer token со scope `calendar:write` и audience `calendar-mcp`.
Для Docker/Kubernetes укажи JSON-массив разрешённых Host в `CALENDAR_MCP_ALLOWED_HOSTS` и адрес JWKS в
`CALENDAR_OIDC_JWKS_URL`.

Текущее memory-хранилище принадлежит только fake-провайдеру и предназначено для одного процесса и
одной реплики. Не увеличивай число Uvicorn workers или Kubernetes replicas до появления общего
хранилища либо реального календарного коннектора.

`actor_id` не принимается от пользователя напрямую. Action Service берёт его из сохранённого Action,
а MCP Gateway удаляет одноимённое поле из недоверенного input и добавляет trusted context. Fake
provider сохраняет значение для теста, а Google provider требует его для поиска подключения.

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
