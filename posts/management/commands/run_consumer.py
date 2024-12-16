from django.core.management.base import BaseCommand
from posts.kafka_consumers import process_rating_event

class Command(BaseCommand):
    help = 'Run Kafka consumer for ratings'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Kafka consumer...")
        process_rating_event()