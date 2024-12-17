from celery import Celery

app = Celery('rateapp')
app.conf.beat_schedule = {
    'process-expired-ratings-every-1-minute': {
        'task': 'posts.tasks.process_expired_ratings',
        'schedule': 60.0,
    },
}