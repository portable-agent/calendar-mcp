# Runbook

## Health check

```http
GET /health
```

Нормальный ответ: HTTP 200 и `{"status":"UP"}`.

## MCP-клиент не подключается

1. Проверь URL `http://host:8080/mcp`.
2. Проверь `/health`.
3. Проверь, что клиент поддерживает Streamable HTTP.
4. Проверь Bearer token: audience `calendar-mcp`, scope `calendar:write`, claim `tenant_id`.
5. Запусти `uv run pytest tests/controller/test_calendar_mcp.py`.

Ответ `401` означает отсутствующий или недействительный токен. Ответ `403` означает, что в токене нет
обязательного scope.

Если сервер отвечает `421`, добавь точный Host или шаблон порта `name:*` в JSON-массиве
`CALENDAR_MCP_ALLOWED_HOSTS`. Не отключай DNS-rebinding protection целиком.

## Google Calendar

1. Проверь `CALENDAR_PROVIDER=google-calendar` и адрес `CALENDAR_CONNECTION_URL`.
2. Для `connection_required` подключи Google Calendar через публичный API Connection Service.
3. Для `connection_ambiguous` не выбирай аккаунт скрытно: пользователь должен выбрать default.
4. Проверь audience `connection-service`, scope `connection:token` и разрешённый `azp` service JWT.
5. Не копируй access token, refresh token или тело ответа Google в issue и логи.

## Не найден часовой пояс

Сервис использует IANA-имена, например `Europe/Moscow` или `UTC`. Пакет `tzdata` закреплён в `uv.lock`,
поэтому проверка одинаково работает в Windows и Linux.

## Test API возвращает 404

Это безопасное поведение по умолчанию. Для локального acceptance-теста укажи:

```text
CALENDAR_TEST_API_ENABLED=true
CALENDAR_TEST_API_KEY=<локальный секрет>
```

Передавай тот же секрет в заголовке `X-Test-Key`. Не включай эту настройку в публичном окружении и не
храни секрет в Git.
