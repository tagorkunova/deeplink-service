from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from app.api.deeplinks import router as deeplinks_router
from app.api.redirect import router as redirect_router
from app.core.logger import setup_logger

logger = setup_logger("deeplink-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info({"event": "SERVICE_STARTED", "service": "deeplink-api"})
    yield
    logger.info({"event": "SERVICE_STOPPED", "service": "deeplink-api"})


app = FastAPI(
    title="DeepLink API Service",
    description="""
## DeepLink Lifecycle Service

Сервис для создания, хранения и управления deeplink-ссылками.

### Сценарий использования

1. **Создать ссылку** — `POST /api/deeplinks` с указанием targetUrl, ttl и payload
2. **Перейти по ссылке** — `GET /d/{code}` — сервис редиректит на targetUrl
3. **Посмотреть статистику** — `GET /api/deeplinks/{id}` — видно clickCount
4. **Деактивировать** — `DELETE /api/deeplinks/{id}`

### Логирование

Все события пишутся в JSON-формате и отправляются в ELK:
- `DEEPLINK_CREATED` — ссылка создана
- `DEEPLINK_OPENED` — пользователь перешёл по ссылке
- `DEEPLINK_REDIRECTED` — редирект выполнен
- `DEEPLINK_EXPIRED` — срок жизни истёк
- `DEEPLINK_DISABLED` — ссылка деактивирована вручную
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "DeepLink Team",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deeplinks_router, prefix="/api/deeplinks", tags=["deeplinks"])
app.include_router(redirect_router, tags=["redirect"])


@app.get("/health", tags=["system"], summary="Проверка состояния сервиса")
def health():
    """Возвращает статус сервиса. Используется для healthcheck в docker-compose."""
    return {"status": "ok", "service": "deeplink-api"}
