import shortuuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.deeplink import DeepLink
from app.models.schemas import DeepLinkCreate, DeepLinkResponse
from app.core.logger import setup_logger

logger = setup_logger("deeplink-api")

BASE_URL = "http://localhost:8080"


def _to_response(link: DeepLink) -> DeepLinkResponse:
    return DeepLinkResponse(
        id=link.id,
        code=link.code,
        targetUrl=link.target_url,
        payload=link.payload or {},
        createdAt=link.created_at,
        expiresAt=link.expires_at,
        active=link.active,
        clickCount=link.click_count,
        shortUrl=f"{BASE_URL}/d/{link.code}",
    )


async def create_deeplink(db: AsyncSession, data: DeepLinkCreate, request_id: str) -> DeepLinkResponse:
    code = shortuuid.ShortUUID().random(length=8)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=data.ttlSeconds)

    link = DeepLink(
        code=code,
        target_url=data.targetUrl,
        payload=data.payload,
        expires_at=expires_at,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)

    logger.info({
        "event": "DEEPLINK_CREATED",
        "deeplinkCode": code,
        "deeplinkId": str(link.id),
        "targetUrl": data.targetUrl,
        "requestId": request_id,
    })

    return _to_response(link)


async def get_deeplink(db: AsyncSession, deeplink_id: str) -> DeepLink | None:
    result = await db.execute(select(DeepLink).where(DeepLink.id == deeplink_id))
    return result.scalar_one_or_none()


async def list_deeplinks(db: AsyncSession) -> list[DeepLink]:
    result = await db.execute(select(DeepLink).order_by(DeepLink.created_at.desc()))
    return list(result.scalars().all())


async def deactivate_deeplink(db: AsyncSession, deeplink_id: str, request_id: str) -> bool:
    result = await db.execute(
        update(DeepLink)
        .where(DeepLink.id == deeplink_id)
        .values(active=False)
        .returning(DeepLink.code)
    )
    await db.commit()
    row = result.fetchone()
    if row:
        logger.info({
            "event": "DEEPLINK_DISABLED",
            "deeplinkCode": row[0],
            "deeplinkId": deeplink_id,
            "requestId": request_id,
        })
        return True
    return False
