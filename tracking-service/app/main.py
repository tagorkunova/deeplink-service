from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.events import router as events_router
from app.api.stats import router as stats_router
from app.core.logger import setup_logger

logger = setup_logger("tracking-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info({"event": "SERVICE_STARTED", "service": "tracking-service"})
    yield
    logger.info({"event": "SERVICE_STOPPED", "service": "tracking-service"})


app = FastAPI(
    title="Redirect Tracking Service",
    description="Сервис отслеживания событий переходов по deeplink",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router, prefix="/api/events", tags=["events"])
app.include_router(stats_router, prefix="/api/stats", tags=["stats"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "tracking-service"}
