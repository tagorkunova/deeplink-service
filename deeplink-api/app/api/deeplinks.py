import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.schemas import DeepLinkCreate, DeepLinkResponse, DeepLinkListResponse
from app.services import deeplink_service

router = APIRouter()


def get_request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID", str(uuid.uuid4()))


@router.post(
    "",
    response_model=DeepLinkResponse,
    status_code=201,
    summary="Создать deeplink",
    description="""
Создаёт новую deeplink-ссылку с уникальным кодом.

**Пример запроса:**
```json
{
  "targetUrl": "https://example.com/promo",
  "ttlSeconds": 3600,
  "payload": {
    "userId": "123",
    "campaign": "spring-sale",
    "source": "email"
  }
}
```

**Возвращает** короткую ссылку вида `http://localhost:8080/d/abc123fg`
    """,
    responses={
        201: {"description": "Deeplink успешно создан"},
        422: {"description": "Ошибка валидации — невалидный URL или ttlSeconds"},
    }
)
async def create_deeplink(
    data: DeepLinkCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    request_id = get_request_id(request)
    return await deeplink_service.create_deeplink(db, data, request_id)


@router.get(
    "",
    response_model=DeepLinkListResponse,
    summary="Список всех deeplink",
    description="Возвращает все созданные ссылки, отсортированные по дате создания (новые первые).",
)
async def list_deeplinks(db: AsyncSession = Depends(get_db)):
    links = await deeplink_service.list_deeplinks(db)
    items = [deeplink_service._to_response(l) for l in links]
    return DeepLinkListResponse(items=items, total=len(items))


@router.get(
    "/{deeplink_id}",
    response_model=DeepLinkResponse,
    summary="Получить deeplink по ID",
    responses={
        200: {"description": "Deeplink найден"},
        404: {"description": "Deeplink не найден"},
    }
)
async def get_deeplink(deeplink_id: str, db: AsyncSession = Depends(get_db)):
    link = await deeplink_service.get_deeplink(db, deeplink_id)
    if not link:
        raise HTTPException(status_code=404, detail="DeepLink not found")
    return deeplink_service._to_response(link)


@router.delete(
    "/{deeplink_id}",
    status_code=204,
    summary="Деактивировать deeplink",
    description="Переводит ссылку в статус inactive. После этого переход по ней вернёт 410 Gone.",
    responses={
        204: {"description": "Ссылка деактивирована"},
        404: {"description": "Deeplink не найден"},
    }
)
async def deactivate_deeplink(
    deeplink_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    request_id = get_request_id(request)
    deleted = await deeplink_service.deactivate_deeplink(db, deeplink_id, request_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="DeepLink not found")
