from typing import Any
from datetime import datetime
from kafka import KafkaConsumer
import json
import uuid

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.sales import Sales

consumer = KafkaConsumer(
    settings.KAFKA_TOPIC_SALES,
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id=settings.KAFKA_GROUP_ID,
)


def consume_sale_events(stop_event):
    while not stop_event.is_set():
        for message in consumer:
            data = message.value
            print(data)
            print("incoming sales data")
            add_sales_record(data)
        if stop_event.is_set():
            break


def add_sales_record(data: Any) -> None:
    db = SessionLocal()
    try:
        sale = Sales(
            order_id=data["order_id"],
            order_item_id=data["order_item_id"],
            product_id=data["product_id"],
            category_id=data["category_id"],
            channel_id=data["channel_id"],
            sale_date=data["sale_date"],
            amount=data["amount"],
        )
        db.add(sale)
        db.commit()
        print("try")
    except Exception as e:
        db.rollback()
        print(f"Failed to create sales record: {e}")
    finally:
        db.close()
