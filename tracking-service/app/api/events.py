import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db
from app.core.logger import setup_logger

router = APIRouter()
logger = setup_logger("tracking-service")


class TrackEventRequest(BaseModel):
    event: str
    deeplinkId: str
    code: str
    userAgent: str = ""
    ip: str = ""
    requestId: str = ""


@router.post("", status_code=201)
async def track_event(data: TrackEventRequest, db: AsyncSession = Depends(get_db)):
    event_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    await db.execute(text("""
        INSERT INTO deeplink_events (id, deeplink_id, event_type, created_at, ip, user_agent, metadata)
        VALUES (:id, :deeplink_id, :event_type, :created_at, :ip, :user_agent, :metadata::jsonb)
    """), {
        "id": event_id,
        "deeplink_id": data.deeplinkId,
        "event_type": data.event,
        "created_at": now,
        "ip": data.ip,
        "user_agent": data.userAgent,
        "metadata": f'{{"requestId": "{data.requestId}"}}',
    })

    await db.execute(text("""
        UPDATE deeplinks SET click_count = click_count + 1 WHERE id = :id
    """), {"id": data.deeplinkId})

    await db.commit()

    logger.info({
        "event": data.event,
        "deeplinkCode": data.code,
        "deeplinkId": data.deeplinkId,
        "ip": data.ip,
        "requestId": data.requestId,
        "timestamp": now.isoformat(),
    })

    return {"status": "tracked", "eventId": event_id}
