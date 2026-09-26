# Архитектура

## Поток команды

```mermaid
sequenceDiagram
    participant Worker as Temporal worker
    participant OIDC as Keycloak
    participant MCP as MCP controller
    participant Service as CalendarService
    participant Repo as CalendarRepository

    Worker->>MCP: tools/call create_event + Bearer token
    MCP->>OIDC: Проверка подписи через JWKS
    OIDC-->>MCP: Публичный ключ
    Note over MCP: tenant_id берётся только из token claim
    MCP->>Service: create(NewEvent)
    Service->>Repo: find(tenant_id, request_key)
    alt Событие уже есть
        Repo-->>Service: старое событие
    else Новая команда
        Service->>Repo: save_if_missing(event)
        Repo-->>Service: сохранённое событие
    end
    Service-->>MCP: CalendarEvent
    MCP-->>Worker: result.eventId
```

## Зависимости папок

```text
controller -> service -> repository
     |           |           |
     v           v           v
  MCP/HTTP     model      connector
```

`model` не импортирует MCP или FastAPI. `service` не знает о HTTP. `repository` отвечает за атомарное
`save_if_missing`, поэтому два одинаковых запуска не создают две встречи.

## Почему request_key обязателен

Temporal может повторить activity после сетевой ошибки. Пара `(tenant_id, request_key)` определяет одну
логическую встречу. Повтор с теми же данными возвращает старый `eventId`; повтор с другими данными
возвращает ошибку конфликта.

`tenant_id` отсутствует во входной схеме MCP tool: вызывающий не может выбрать чужого tenant. Контроллер
получает его из проверенного OIDC-токена. Токен обязан иметь audience `calendar-mcp` и scope
`calendar:write`.

`actor_id` передаётся отдельно от бизнес-payload как trusted execution context. Он может отсутствовать
у старого fake-вызова, но Google provider обязан отклонить выполнение без владельца подключения.

Memory repository обеспечивает атомарность только внутри одного процесса. Пока он используется,
разрешены один Uvicorn worker и одна реплика сервиса. Масштабирование начнётся после подключения общего
хранилища или провайдера с idempotency key.

## Test API

`GET /test/events?requestKey=...` нужен только acceptance-тесту. Он выключен по умолчанию и при
включении требует заголовок `X-Test-Key`. MCP endpoint остаётся `/mcp`, health check — `/health`.
