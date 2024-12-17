from celery import shared_task
from django.core.cache import cache
import time
import json

@shared_task
def process_expired_ratings():
    redis_client = cache.client.get_client()
    current_time = time.time()
    five_minutes_ago = current_time - 300

    for key in redis_client.keys("post:*:rating_buffer"):
        post_id = key.split(':')[1]

        expired_ratings = redis_client.zrangebyscore(key, '-inf', five_minutes_ago)
        if not expired_ratings:
            continue

        total_ratings = int(redis_client.get(f'post:{post_id}:total_ratings') or 0)
        total_score = int(redis_client.get(f'post:{post_id}:total_score') or 0)

        for rating_data in expired_ratings:
            rating = json.loads(rating_data)
            total_score += int(rating['score'])
            total_ratings += 1

        redis_client.set(f'post:{post_id}:total_ratings', total_ratings, ex=3600)
        redis_client.set(f'post:{post_id}:total_score', total_score, ex=3600)
        average_rating = total_score / total_ratings
        redis_client.set(f'post:{post_id}:avg_rating', average_rating, ex=3600)

        redis_client.zremrangebyscore(key, '-inf', five_minutes_ago)
        print(f"Applied ratings for post {post_id} and updated average to {average_rating}")