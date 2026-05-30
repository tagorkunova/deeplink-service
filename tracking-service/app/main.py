from fastapi import FastAPI

app = FastAPI(
    title="Redirect Tracking Service",
    description="TODO: реализовать сервис трекинга событий переходов",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "tracking-service"}


# TODO: реализовать POST /api/events — сохранить событие перехода
# TODO: реализовать GET /api/stats/{deeplink_id} — статистика по ссылке
