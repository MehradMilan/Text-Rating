from rest_framework import serializers
from .models import Post, Rating
from django.contrib.auth.models import User
from django.core.cache import cache

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'post', 'score']

class PostSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'average_rating']

    def get_average_rating(self, obj):
        cached_rating = cache.get(f'post:{obj.id}:avg_rating')
        if cached_rating is not None:
            return cached_rating

        ratings = obj.ratings.all()
        return sum(rating.score for rating in ratings) / ratings.count() if ratings.exists() else 0


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user