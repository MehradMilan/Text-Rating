from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import time
import json

RETRY_LIMIT = 5
SLEEP_INTERVAL = 5

producer = None

def get_producer():
    global producer
    if producer is None:
        for attempt in range(RETRY_LIMIT):
            try:
                producer = KafkaProducer(
                    bootstrap_servers='kafka:9092',
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                break
            except NoBrokersAvailable as e:
                if attempt < RETRY_LIMIT - 1:
                    print("Kafka broker not available, retrying...")
                    time.sleep(SLEEP_INTERVAL)
                else:
                    raise Exception("Kafka broker is not available after retries.") from e
    return producer

def send_rating_event(post_id, score, user_id):
    event = {
        'post_id': post_id,
        'score': score,
        'user_id': user_id
    }
    producer = get_producer()
    producer.send('ratings', event)