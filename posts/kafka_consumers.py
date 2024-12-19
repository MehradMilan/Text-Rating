from kafka import KafkaConsumer
import json
from django.core.cache import cache
import time

consumer = KafkaConsumer(
    'ratings',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='analytics_consumers',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def store_rating_in_buffer(post_id, score, user_id):
    redis_client = cache.client.get_client()
    current_time = time.time()
    rating_data = json.dumps({"user_id": user_id, "score": score, "timestamp": current_time})

    redis_client.zadd(f'post:{post_id}:rating_buffer', {rating_data: current_time})

def process_rating_event():
    for message in consumer:
        event = message.value
        post_id = event['post_id']
        score = event['score']
        user_id = event['user_id']

        store_rating_in_buffer(post_id, score, user_id)