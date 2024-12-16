from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_rating_event(post_id, score, user_id):
    event = {
        'post_id': post_id,
        'score': score,
        'user_id': user_id
    }
    producer.send('ratings', event)