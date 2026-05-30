"""
Интеграционный тест: полный сценарий жизни deeplink.
Запуск: pytest tests/test_integration.py -v
Требует запущенного docker-compose.
"""
import pytest
import httpx

API_URL = "http://localhost:8080"


@pytest.mark.asyncio
async def test_create_deeplink():
    # TODO: реализовать тест создания deeplink
    pass


@pytest.mark.asyncio
async def test_redirect():
    # TODO: реализовать тест перехода по ссылке
    pass


@pytest.mark.asyncio
async def test_expired_deeplink():
    # TODO: реализовать тест истёкшей ссылки
    pass


@pytest.mark.asyncio
async def test_invalid_url():
    # TODO: реализовать тест валидации URL
    pass
