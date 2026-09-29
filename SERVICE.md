# Calendar MCP

## Ответственность

Сервис выполняет уже подтверждённые команды календаря. Он проверяет вход, выбирает настроенный
календарный provider и возвращает идентификатор события.

## API

| Тип | Адрес | Назначение |
| --- | --- | --- |
| MCP Streamable HTTP | `/mcp` | Tool `create_event` |
| HTTP | `/health` | Проверка процесса |
| HTTP, только test mode | `/test/events` | Проверка fake-событий в acceptance-тесте |

Исходящий internal HTTP-контракт Connection Service берётся из `portable-agent/contracts` v2.7.0.
Клиент использует только `POST /internal/v1/tokens`; отдельная копия DTO в сервисе не создаётся.

## Что сервис делает

- получает `tenant_id` только из проверенного OIDC-токена;
- получает доверенный `actor_id` через MCP Gateway;
- проверяет данные события;
- передаёт команду выбранному `CalendarProvider`;
- защищает fake-календарь от дублей по `tenant_id + request_key`.

## Что сервис не делает

- не распознаёт пользовательский текст;
- не решает, нужно ли подтверждение;
- не хранит action workflow;
- не хранит OAuth refresh token;
- не принимает tenant из аргументов tool.

## Текущее состояние

Работают две стратегии:

- `FakeCalendar` с memory-хранилищем для CI и локальной разработки;
- `GoogleCalendar`, который получает короткоживущий access token у Connection Service и вызывает
  Google Calendar API.

Стратегия выбирается через `CALENDAR_PROVIDER`. Google provider требует `actor_id`, не хранит token и
использует стабильный base32hex event ID для безопасного повтора команды.

## Настройки и проверки

Переменные окружения и команды находятся в [README.md](README.md). Детальная схема слоёв находится в
[docs/architecture.md](docs/architecture.md).
