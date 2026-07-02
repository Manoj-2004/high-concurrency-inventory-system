import json
import socket

from kafka import KafkaConsumer
from app.logging_config import logger

from app.services.kafka_purchase_service import process_purchase_event
from app.config import settings


CONSUMER_ID = socket.gethostname()

consumer = KafkaConsumer(
    "purchase-events",
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="inventory-workers",
)

logger.info(f"Consumer {CONSUMER_ID} waiting for purchase events...")

for message in consumer:
    try:
        process_purchase_event(message.value)
        consumer.commit()
        logger.info(f"Consumer {CONSUMER_ID} committed offset successfully")

    except Exception as error:
        logger.error(f"Error processing message: {error}")
        logger.warning("Offset not committed. Kafka will retry this message after restart.")
        break