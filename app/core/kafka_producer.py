from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
import json
import datetime
import decimal
import uuid

from app.core.config import settings


def create_topics():
    """create topics on kafka if not exist"""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS, client_id="admin-client"
        )

        existing_topics = admin_client.list_topics()

        required_topics = [
            settings.KAFKA_TOPIC_ORDER,
            settings.KAFKA_TOPIC_SALES,
        ]
        topic_list = []
        for topic_name in required_topics:
            if topic_name and topic_name not in existing_topics:
                print(f"Creating topic: {topic_name}")
                topic_list.append(
                    NewTopic(
                        name=topic_name,
                        num_partitions=1,
                        replication_factor=1,
                    )
                )
            else:
                if topic_name:
                    print(f"Topic {topic_name} already exists")

        if topic_list:
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print("Topics created successfully")

        admin_client.close()

    except Exception as e:
        print(f"Error creating Kafka topics: {e}")


create_topics()

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v, default=default_serializer).encode(
        "utf-8"
    ),
    connections_max_idle_ms=10000,
    request_timeout_ms=30000,
    metadata_max_age_ms=10000,
    retry_backoff_ms=1000,
)


def default_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def on_success(record_metadata):
    print(
        f"Message sent to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}"
    )


def on_error(excp):
    print(f"Failed to send message: {excp}")


async def send_order_event(event_data) -> None:
    serialized_data = json.loads(json.dumps(event_data, default=default_serializer))

    try:
        future = producer.send(settings.KAFKA_TOPIC_ORDER, serialized_data)
        future.add_callback(on_success)
        future.add_errback(on_error)
        producer.flush()
    except Exception as e:
        print(f"Kafka connection/send failed: {e}")


def send_sales_event(event_data) -> None:
    serialized_data = json.loads(json.dumps(event_data, default=default_serializer))
    try:
        future = producer.send(settings.KAFKA_TOPIC_SALES, serialized_data)
        future.add_callback(on_success)
        future.add_errback(on_error)
        producer.flush()
    except Exception as e:
        print(f"Kafka connection/send failed: {e}")