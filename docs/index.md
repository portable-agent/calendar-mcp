# Calendar MCP

Сервис предоставляет стандартный MCP tool `create_event`. Он нужен Temporal worker внутри Portable
Agent и будущим совместимым MCP-клиентам.

Текущая версия — fake-calendar для первого вертикального сценария. Данные живут в памяти процесса и
не предназначены для production. Настоящие провайдеры будут отдельными repository-адаптерами.

## Вход MCP tool

`create_event` принимает обязательные поля `tenant_id`, `request_key`, `title`, `start_at`, `end_at` и
`time_zone`. Поля `description` и `attendees` необязательны. Успешный ответ содержит `eventId`.
