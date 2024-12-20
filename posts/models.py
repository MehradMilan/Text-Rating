from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('user', 'post')

class PostAverageRating(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='average_rating_entry')
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)

    def update_average(self):
        if self.total_ratings > 0:
            self.average_rating = self.total_score / self.total_ratings
        else:
            self.average_rating = 0.0
        self.save()