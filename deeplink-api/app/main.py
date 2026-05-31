from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.deeplinks import router as deeplinks_router
from app.core.logger import setup_logger

logger = setup_logger("deeplink-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info({"event": "SERVICE_STARTED", "service": "deeplink-api"})
    yield
    logger.info({"event": "SERVICE_STOPPED", "service": "deeplink-api"})


app = FastAPI(
    title="DeepLink API Service",
    description="Сервис создания и управления deeplink-ссылками",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deeplinks_router, prefix="/api/deeplinks", tags=["deeplinks"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "deeplink-api"}
