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
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'average_rating', 'user_rating']

    def get_average_rating(self, obj):
        cached_rating = cache.get(f'post:{obj.id}:avg_rating')
        if cached_rating is not None:
            return cached_rating

        ratings = obj.ratings.all()
        average_rating = sum(rating.score for rating in ratings) / ratings.count() if ratings.exists() else 0

        cache.set(f'post:{obj.id}:avg_rating', average_rating, timeout=3600)
        return average_rating

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_rating = Rating.objects.filter(post=obj, user=request.user).first()
            return user_rating.score if user_rating else None
        return None

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