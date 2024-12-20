from celery import shared_task
from django.core.cache import cache
import time
import json
from .models import PostAverageRating

@shared_task
def process_expired_ratings():
    redis_client = cache.client.get_client()
    current_time = time.time()
    two_minutes_ago = current_time - 120

    for key in redis_client.keys("post:*:rating_buffer"):
        post_id = key.decode('utf-8').split(':')[1]

        expired_ratings = redis_client.zrangebyscore(key, '-inf', two_minutes_ago)
        if not expired_ratings:
            continue

        post_avg_rating, _ = PostAverageRating.objects.get_or_create(post_id=post_id)

        for rating_data in expired_ratings:
            rating = json.loads(rating_data)
            post_avg_rating.total_score += int(rating['score'])
            post_avg_rating.total_ratings += 1

        post_avg_rating.update_average()

        redis_client.zremrangebyscore(key, '-inf', two_minutes_ago)