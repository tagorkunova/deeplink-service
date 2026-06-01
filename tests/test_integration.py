"""
Интеграционный тест: полный сценарий жизни deeplink.
Запуск: pytest tests/test_integration.py -v
Требует запущенного docker-compose: docker-compose up --build
"""
import pytest
import httpx
import time

API_URL = "http://localhost:8080"


@pytest.mark.asyncio
async def test_full_deeplink_lifecycle():
    async with httpx.AsyncClient(base_url=API_URL, follow_redirects=False) as client:

        # 1. Создаём deeplink
        response = await client.post("/api/deeplinks", json={
            "targetUrl": "https://example.com/promo",
            "ttlSeconds": 3600,
            "payload": {"userId": "test-123", "campaign": "integration-test"},
        })
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        link = response.json()
        assert link["code"]
        assert link["active"] is True
        assert link["clickCount"] == 0
        assert link["targetUrl"] == "https://example.com/promo"
        assert link["payload"]["userId"] == "test-123"
        code = link["code"]
        deeplink_id = link["id"]

        # 2. Получаем информацию по ID
        response = await client.get(f"/api/deeplinks/{deeplink_id}")
        assert response.status_code == 200
        assert response.json()["code"] == code

        # 3. Список ссылок содержит созданную
        response = await client.get("/api/deeplinks")
        assert response.status_code == 200
        ids = [item["id"] for item in response.json()["items"]]
        assert deeplink_id in ids

        # 4. Переход по ссылке — должен редиректить
        response = await client.get(f"/d/{code}")
        assert response.status_code == 302, f"Expected redirect 302, got {response.status_code}"
        assert response.headers["location"] == "https://example.com/promo"

        # 5. Счётчик кликов вырос
        time.sleep(1)
        response = await client.get(f"/api/deeplinks/{deeplink_id}")
        assert response.json()["clickCount"] >= 1, "clickCount должен вырасти после перехода"

        # 6. Деактивируем ссылку
        response = await client.delete(f"/api/deeplinks/{deeplink_id}")
        assert response.status_code == 204

        # 7. Переход по деактивированной ссылке — ошибка
        response = await client.get(f"/d/{code}")
        assert response.status_code == 410, f"Expected 410 Gone, got {response.status_code}"


@pytest.mark.asyncio
async def test_expired_deeplink():
    async with httpx.AsyncClient(base_url=API_URL, follow_redirects=False) as client:

        # Создаём ссылку с TTL 1 секунда
        response = await client.post("/api/deeplinks", json={
            "targetUrl": "https://example.com/short-lived",
            "ttlSeconds": 1,
            "payload": {},
        })
        assert response.status_code == 201
        code = response.json()["code"]

        # Ждём истечения
        time.sleep(2)

        # Ссылка должна вернуть 410
        response = await client.get(f"/d/{code}")
        assert response.status_code == 410, f"Expected 410, got {response.status_code}"


@pytest.mark.asyncio
async def test_invalid_url_rejected():
    async with httpx.AsyncClient(base_url=API_URL) as client:
        response = await client.post("/api/deeplinks", json={
            "targetUrl": "not-a-url",
            "ttlSeconds": 3600,
        })
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_nonexistent_deeplink_returns_404():
    async with httpx.AsyncClient(base_url=API_URL, follow_redirects=False) as client:
        response = await client.get("/d/nonexistent000")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_deeplink_not_found_by_id():
    async with httpx.AsyncClient(base_url=API_URL) as client:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/deeplinks/{fake_id}")
        assert response.status_code == 404
