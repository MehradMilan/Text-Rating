from django.apps import AppConfig
import sys
from datetime import datetime, timedelta
from django.utils.timezone import now

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'

    def ready(self):
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        if not 'runserver' in sys.argv:
            return
        from django.db.utils import OperationalError
        try:
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=2,
                period=IntervalSchedule.MINUTES,
            )

            start_time = now() + timedelta(seconds=30)

            PeriodicTask.objects.update_or_create(
                name="Process Expired Ratings",
                defaults={
                    'interval': schedule,
                    'task': "posts.tasks.process_expired_ratings",
                    'start_time': start_time,
                }
            )
        except OperationalError:
            pass