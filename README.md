# DeepLink Lifecycle Service

Учебный проект: сервис для создания, хранения и управления deeplink-ссылками с параметрами, временем жизни и полной наблюдаемостью через ELK.

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

## Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| deeplink-api | 8080 | Основной REST API + редирект |
| tracking-service | 8081 | Трекинг событий переходов |
| expiration-worker | — | Фоновый воркер истечения ссылок |
| frontend | 3000 | Web-интерфейс управления |
| PostgreSQL | 5432 | База данных |
| Elasticsearch | 9200 | Хранилище логов |
| Logstash | 5044 | Сборщик логов |
| Kibana | 5601 | Визуализация логов |

## Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/tagorkunova/deeplink-service.git
cd deeplink-service

# Запустить все сервисы
docker-compose up --build
```

После запуска открыть в браузере:

| Что | Адрес |
|-----|-------|
| Веб-интерфейс | http://localhost:3000 |
| API документация (Swagger) | http://localhost:8080/docs |
| Kibana | http://localhost:5601 |

## API

### Создать deeplink
```
POST /api/deeplinks
{
  "targetUrl": "https://example.com/promo",
  "ttlSeconds": 3600,
  "payload": { "userId": "123", "campaign": "spring-sale", "source": "email" }
}
```

### Перейти по ссылке
```
GET /d/{code}
→ 302 redirect на targetUrl (если ссылка активна)
→ 410 если истекла или деактивирована
→ 404 если не найдена
```

### Остальные endpoints
```
GET    /api/deeplinks         — список всех ссылок
GET    /api/deeplinks/{id}    — получить ссылку по ID
DELETE /api/deeplinks/{id}    — деактивировать ссылку
GET    /health                — healthcheck
```

## Логирование

Все сервисы пишут структурированные JSON-логи которые поступают в ELK:

```json
{
  "timestamp": "2026-05-31T10:05:00Z",
  "level": "INFO",
  "event": "DEEPLINK_OPENED",
  "deeplinkCode": "abc123fg",
  "deeplinkId": "uuid",
  "service": "deeplink-api",
  "requestId": "uuid"
}
```

Типы событий: `DEEPLINK_CREATED`, `DEEPLINK_OPENED`, `DEEPLINK_REDIRECTED`, `DEEPLINK_EXPIRED`, `DEEPLINK_DISABLED`

## Тесты

```bash
# Unit-тесты (без docker)
cd deeplink-api
pip install -r requirements.txt
pytest tests/ -v

# Интеграционные тесты (требует запущенного docker-compose)
pip install pytest pytest-asyncio httpx
pytest tests/test_integration.py -v
```

## Структура проекта

```
deeplink-service/
├── deeplink-api/          # REST API сервис (Python/FastAPI)
│   ├── app/
│   │   ├── api/           # HTTP роутеры
│   │   ├── core/          # Логгер
│   │   ├── db/            # Подключение к БД
│   │   ├── models/        # ORM модели и Pydantic схемы
│   │   └── services/      # Бизнес-логика
│   └── tests/             # Unit-тесты
├── tracking-service/      # Сервис трекинга событий (Python/FastAPI)
├── expiration-worker/     # Воркер истечения ссылок (Python/asyncio)
├── frontend/              # Web-интерфейс (HTML/JS + Nginx)
├── elk/logstash/          # Конфигурация Logstash
├── tests/                 # Интеграционные тесты
├── init.sql               # Схема базы данных
└── docker-compose.yml     # Оркестрация всех сервисов
```
