from kafka import KafkaConsumer
import json
from django.core.cache import cache

consumer = KafkaConsumer(
    'ratings',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='analytics_consumers',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def process_rating_event():
    redis_client = cache.client.get_client()
    for message in consumer:
        event = message.value
        post_id = event['post_id']
        score = event['score']

        print(f"Processing event: {event}")

        total_ratings_key = f'post:{post_id}:total_ratings'
        total_ratings = redis_client.get(total_ratings_key) or 0
        total_ratings = int(total_ratings) + 1
        redis_client.set(total_ratings_key, total_ratings, ex=3600)

        total_score_key = f'post:{post_id}:total_score'
        total_score = redis_client.get(total_score_key) or 0
        total_score = int(total_score) + score
        redis_client.set(total_score_key, total_score, ex=3600)

        average_rating = total_score / total_ratings
        redis_client.set(f'post:{post_id}:avg_rating', average_rating, ex=3600)

        redis_client.zincrby('most_rated_posts', 1, f'post:{post_id}')