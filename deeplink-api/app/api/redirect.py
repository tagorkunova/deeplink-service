import uuid
import httpx
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.deeplink import DeepLink
from app.core.logger import setup_logger

router = APIRouter()
logger = setup_logger("deeplink-api")

TRACKING_SERVICE_URL = "http://tracking-service:8081"


async def get_deeplink_by_code(db: AsyncSession, code: str) -> DeepLink | None:
    result = await db.execute(select(DeepLink).where(DeepLink.code == code))
    return result.scalar_one_or_none()


@router.get("/d/{code}")
async def open_deeplink(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    request_id = str(uuid.uuid4())
    link = await get_deeplink_by_code(db, code)

    if not link:
        return HTMLResponse(content=_error_page("Ссылка не найдена", "Такой deeplink не существует"), status_code=404)

    now = datetime.now(timezone.utc)

    if not link.active or link.expires_at < now:
        logger.info({
            "event": "DEEPLINK_EXPIRED",
            "deeplinkCode": code,
            "deeplinkId": str(link.id),
            "requestId": request_id,
        })
        return HTMLResponse(content=_error_page("Ссылка истекла", "Срок действия этой ссылки истёк."), status_code=410)

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(f"{TRACKING_SERVICE_URL}/api/events", json={
                "event": "DEEPLINK_OPENED",
                "deeplinkId": str(link.id),
                "code": code,
                "userAgent": request.headers.get("user-agent", ""),
                "ip": request.client.host if request.client else "",
                "requestId": request_id,
            })
    except Exception as e:
        logger.warning(f"Could not notify tracking service: {e}")

    logger.info({
        "event": "DEEPLINK_REDIRECTED",
        "deeplinkCode": code,
        "deeplinkId": str(link.id),
        "targetUrl": link.target_url,
        "requestId": request_id,
    })

    return RedirectResponse(url=link.target_url, status_code=302)


def _error_page(title: str, message: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>{title}</title>
<style>
  body {{ font-family: sans-serif; display: flex; align-items: center; justify-content: center;
         height: 100vh; margin: 0; background: #f5f5f5; }}
  .box {{ text-align: center; background: white; padding: 2rem 3rem;
          border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
  h1 {{ color: #e53e3e; }}
  p {{ color: #666; }}
  a {{ color: #3182ce; text-decoration: none; }}
</style>
</head>
<body>
  <div class="box">
    <h1>⚠️ {title}</h1>
    <p>{message}</p>
    <a href="/">← Вернуться на главную</a>
  </div>
</body>
</html>"""
