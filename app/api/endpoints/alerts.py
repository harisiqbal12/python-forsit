from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import settings
from fastapi import Request
from app.db.redis import get_redis_sub
import time

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    responses={404: {"detail": "Not found"}},
)


@router.get("/low-stock")
async def get_low_stock_alerts():
    def event_generator():
        pubsub = get_redis_sub().pubsub()
        pubsub.subscribe(settings.REDIS_LOW_INVENTORY)
        yield 'data: {"status": "connected"}\n\n'
        try:
            for message in pubsub.listen():
                if message["type"] == "message":
                    yield f"data: {message['data'].decode('utf-8')}\n\n"
                time.sleep(0.01)
        finally:
            pubsub.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/incoming-order")
async def incoming_order_alerts():
    def event_generator():
        pubsub = get_redis_sub().pubsub()
        pubsub.subscribe(settings.REDIS_INCOMING_ORDER)
        yield 'data: {"status": "connected"}\n\n'
        try:
            for message in pubsub.listen():
                if message["type"] == "message":
                    yield f"data: {message['data'].decode('utf-8')}\n\n"
                time.sleep(0.01)
        finally:
            pubsub.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
