import asyncio
import os

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))


async def main():
    print(f"Expiration worker started. Check interval: {CHECK_INTERVAL}s")
    while True:
        # TODO: найти истекшие ссылки в БД и пометить их как inactive
        # TODO: записать событие DEEPLINK_EXPIRED для каждой истекшей ссылки
        # TODO: логировать результат в JSON-формате
        print("TODO: checking for expired deeplinks...")
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
