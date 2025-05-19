from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.kafka_order_consumer import (
    consume_order_events,
    listen_and_process_snapshot_queue,
)
from app.core.kafka_sale_consumer import consume_sale_events

from app.core.config import settings
from app.api.endpoints import (
    users,
    products,
    category,
    inventory,
    sales_channel,
    orders,
    alerts,
    sales
)
import threading

stop_event = threading.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("lifespan")
    """Lifespan context manager for the FastAPI app"""
    consumer_thread = threading.Thread(target=consume_order_events, args=(stop_event,))
    consumer_thread.daemon = True
    consumer_thread.start()

    consumer_sales_thread = threading.Thread(
        target=consume_sale_events, args=(stop_event,)
    )
    consumer_sales_thread.daemon = True
    consumer_sales_thread.start()

    snapshot_queue_thread = threading.Thread(target=listen_and_process_snapshot_queue)
    snapshot_queue_thread.daemon = True
    snapshot_queue_thread.start()

    yield

    stop_event.set()
    consumer_thread.join()
    consumer_sales_thread.join()
    snapshot_queue_thread.join()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(category.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)
app.include_router(sales_channel.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(sales.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to the forsit assignment"}


@app.exception_handler(IntegrityError)
async def integerity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400, content={"detail": "A DB integerity error occured"}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500, content=({"detail": "An unexpected error occured"})
    )
