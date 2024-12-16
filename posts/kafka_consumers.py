from kafka import KafkaConsumer
import json
from .models import Rating
from .views import update_average_rating

consumer = KafkaConsumer(
    'ratings',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='rating_consumers',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def process_rating_event():
    for message in consumer:
        event = message.value
        post_id = event['post_id']
        score = event['score']
        user_id = event['user_id']

        # Log the received event
        print(f"Processing event: {event}")

        # Update the average rating in cache
        update_average_rating(post_id)