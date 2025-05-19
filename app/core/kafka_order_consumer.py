from datetime import datetime
from kafka import KafkaConsumer
import json
import uuid
from typing import Any
import time

from app.core.config import settings
from app.db.redis import get_redis
from app.db.session import SessionLocal
from app.models.inventory import Inventory
from app.models.sales_snapshot import SalesSnapshot
from app.schema.inventory import InventoryDetails as InventoryDetailsSchema


consumer = KafkaConsumer(
    settings.KAFKA_TOPIC_ORDER,
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id=settings.KAFKA_GROUP_ID,
)


def consume_order_events(stop_event):
    while not stop_event.is_set():
        for message in consumer:
            order_data = message.value
            print("Received order event:", order_data)
            publish_redis_event(data=order_data, channel=settings.REDIS_INCOMING_ORDER)
            send_orders_queue_for_snapshot(
                data=order_data, name=settings.REDIS_QUEUE_ORDER
            )
            for item in order_data.get("items", []):
                product_id = item.get("product_id")
                inventory_detail = get_product_stock(product_id)
                if inventory_detail.quantity <= 20:
                    publish_redis_event(
                        data=inventory_detail, channel=settings.REDIS_LOW_INVENTORY
                    )
                    print("Low stock warning: " + product_id)
            if stop_event.is_set():
                break


def get_product_stock(product_id: str) -> InventoryDetailsSchema:
    db = SessionLocal()
    try:
        inventory = (
            db.query(Inventory).filter(Inventory.product_id == product_id).first()
        )
        if inventory:
            return InventoryDetailsSchema.model_validate(
                inventory, from_attributes=True
            )
        return None
    except Exception as e:
        print(f"Error fetching product stock")
        return None
    finally:
        db.close()


def default_redis_serializer(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return str(datetime)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def publish_redis_event(data: Any, channel: str) -> None:
    redis = get_redis()

    try:
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        redis.publish(channel, json.dumps(data, default=default_redis_serializer))
        print("publish to redis channel: ", channel)
    except Exception as e:
        print(e)
        print("unable to publish event to redis channel")


def send_orders_queue_for_snapshot(data: Any, name: str) -> None:
    redis = get_redis()
    print("pushing to redis queue: ", name)
    try:
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        redis.rpush(name, json.dumps(data, default=default_redis_serializer))
        print(f"Pushed order to Redis queue: {name}")
    except Exception as e:
        print(f"Kafka connection/send failed: {e}")


def listen_and_process_snapshot_queue() -> None:
    redis = get_redis()
    while True:
        queue_length = redis.llen(settings.REDIS_QUEUE_ORDER)
        print("queue length: ", queue_length)
        if queue_length >= 10:
            orders = []
            for _ in range(10):
                order_json = redis.lpop(settings.REDIS_QUEUE_ORDER)
                if order_json:
                    orders.append(json.loads(order_json))
            process_orders(orders)
        else:
            time.sleep(5)


def process_orders(orders: Any) -> None:
    print(f"Processing batch of 10 orders: {orders}")
    total_sales = len(orders)
    total_revenue = 0.0
    total_tax = 0.0
    total_shipping = 0.0
    total_discount = 0.0
    total_quantity = 0
    product_ids = set()

    for order in orders:
        total_revenue += float(order.get("total_amount", 0))
        total_tax += float(order.get("tax_amount", 0))
        total_shipping += float(order.get("shipping_amount", 0))
        total_discount += float(order.get("discount_amount", 0))
        for item in order.get("items", []):
            total_quantity += item.get("quantity", 0)
            product_ids.add(item.get("product_id"))

    total_products = len(product_ids)
    average_sales = total_sales
    average_revenue = total_revenue / total_sales if total_sales else 0
    db = SessionLocal()
    try:
        snapshot = SalesSnapshot(
            total_sales=total_sales,
            total_revenue=total_revenue,
            average_sales=average_sales,
            average_revenue=average_revenue,
            total_quantity=total_quantity,
            total_products=total_products,
            total_tax=total_tax,
            total_shipping=total_shipping,
            total_discount=total_discount,
            interval="batch-10",
        )
        db.add(snapshot)
        db.commit()
        print("Sales snapshot saved to DB.")
    except Exception as e:
        db.rollback()
        print(f"Failed to save sales snapshot: {e}")
    finally:
        db.close()

    return None
