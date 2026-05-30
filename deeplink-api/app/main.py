from fastapi import FastAPI

app = FastAPI(
    title="DeepLink API Service",
    description="TODO: реализовать REST API для управления deeplink-ссылками",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "deeplink-api"}


# TODO: реализовать POST /api/deeplinks — создание ссылки
# TODO: реализовать GET /api/deeplinks — список ссылок
# TODO: реализовать GET /api/deeplinks/{id} — получить ссылку
# TODO: реализовать DELETE /api/deeplinks/{id} — деактивировать ссылку
# TODO: реализовать GET /d/{code} — редирект по коду
