import json

from kafka import KafkaProducer

from app.config import settings

producer = KafkaProducer(
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_serializer=lambda value: json.dumps(value).encode('utf-8') 
)

def publish_purchase_event(event: dict):
    producer.send(settings.kafka_purchase_topic, event)
    producer.flush()
    
def publish_dlq_event(event: dict):
    producer.send(settings.DLQ_topic, event)
    producer.flush()