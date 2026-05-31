from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.database import get_db

router = APIRouter()


@router.get("/{deeplink_id}")
async def get_stats(deeplink_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT event_type, COUNT(*) as count
        FROM deeplink_events
        WHERE deeplink_id = :id
        GROUP BY event_type
    """), {"id": deeplink_id})
    rows = result.fetchall()
    return {
        "deeplinkId": deeplink_id,
        "events": {row[0]: row[1] for row in rows},
    }
