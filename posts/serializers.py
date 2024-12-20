from rest_framework import serializers
from .models import Post, Rating
from django.contrib.auth.models import User
from django.core.cache import cache
from .models import PostAverageRating

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
        try:
            return obj.average_rating_entry.average_rating
        except PostAverageRating.DoesNotExist:
            return 0.0

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