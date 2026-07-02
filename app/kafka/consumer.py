import json

from kafka import KafkaConsumer

from app.services.kafka_purchase_service import process_purchase_event


consumer = KafkaConsumer(
    "purchase-events",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="inventory-workers",
)

print("Waiting for purchase events...\n")

for message in consumer:
    try:
        process_purchase_event(message.value)
        consumer.commit()
        print("Offset committed successfully")

    except Exception as error:
        print(f"Error processing message: {error}")
        print("Offset not committed. Kafka will retry this message after restart.")
        break