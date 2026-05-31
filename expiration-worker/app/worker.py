import asyncio
import os
import json
import sys
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://deeplink_user:deeplink_pass@localhost:5432/deeplink_db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))


class JSONFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, dict):
            data = record.msg
        else:
            data = {"message": record.getMessage()}
        data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        data.setdefault("level", record.levelname)
        data.setdefault("service", "expiration-worker")
        return json.dumps(data, ensure_ascii=False)


logger = logging.getLogger("expiration-worker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)


async def expire_links(session: AsyncSession):
    now = datetime.now(timezone.utc)

    result = await session.execute(text("""
        UPDATE deeplinks
        SET active = FALSE
        WHERE active = TRUE AND expires_at < :now
        RETURNING id, code
    """), {"now": now})

    expired = result.fetchall()
    await session.commit()

    for row in expired:
        deeplink_id, code = row[0], row[1]

        await session.execute(text("""
            INSERT INTO deeplink_events (id, deeplink_id, event_type, created_at, metadata)
            VALUES (gen_random_uuid(), :deeplink_id, 'DEEPLINK_EXPIRED', :now, '{}')
        """), {"deeplink_id": deeplink_id, "now": now})

        logger.info({
            "event": "DEEPLINK_EXPIRED",
            "deeplinkCode": code,
            "deeplinkId": str(deeplink_id),
        })

    await session.commit()

    logger.info({
        "event": "EXPIRATION_RUN",
        "expiredCount": len(expired),
        "checkedAt": now.isoformat(),
    })


async def main():
    engine = create_async_engine(ASYNC_DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    logger.info({"event": "WORKER_STARTED", "checkIntervalSeconds": CHECK_INTERVAL})

    while True:
        try:
            async with AsyncSessionLocal() as session:
                await expire_links(session)
        except Exception as e:
            logger.error({"event": "WORKER_ERROR", "error": str(e)})

        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
