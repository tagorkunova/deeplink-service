# DeepLink Lifecycle Service

Учебный проект: сервис для создания, хранения и управления deeplink-ссылками с параметрами, временем жизни и наблюдаемостью через ELK.

## Архитектура

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│    Frontend      │────▶│   DeepLink API       │────▶│  Tracking Service   │
│  (port 3000)    │     │   (port 8080)        │     │    (port 8081)      │
└─────────────────┘     └──────────┬───────────┘     └──────────┬──────────┘
                                   │                             │
                         ┌─────────▼─────────┐                  │
                         │    PostgreSQL      │◀─────────────────┘
                         │    (port 5432)    │
                         └───────────────────┘
                                   ▲
                         ┌─────────┴─────────┐
                         │ Expiration Worker  │
                         └───────────────────┘

Логи → Logstash (5044) → Elasticsearch (9200) → Kibana (5601)
```

## Сервисы и ответственные

| Сервис | Порт | Кто реализует |
|--------|------|---------------|
| deeplink-api | 8080 | Человек 2 |
| tracking-service | 8081 | Человек 3 |
| expiration-worker | — | Человек 3 |
| frontend | 3000 | Человек 4 |
| docker-compose + ELK | — | Человек 1 |

## Запуск

```bash
docker-compose up --build
```

## Ссылки

| Что | Адрес |
|-----|-------|
| Фронтенд | http://localhost:3000 |
| API docs (Swagger) | http://localhost:8080/docs |
| Kibana | http://localhost:5601 |

## Структура проекта

```
deeplink-service/
├── deeplink-api/          # REST API сервис
├── tracking-service/      # Сервис трекинга событий
├── expiration-worker/     # Воркер истечения ссылок
├── frontend/              # Web-интерфейс
├── elk/logstash/          # Конфигурация Logstash
├── tests/                 # Интеграционные тесты
├── init.sql               # Схема базы данных
└── docker-compose.yml     # Оркестрация сервисов
```
