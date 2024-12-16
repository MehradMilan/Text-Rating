from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Rating
from .serializers import PostSerializer, RatingSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from .pagination import CustomPagination
from django.db.models import Avg

class PostList(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        cached_posts = cache.get('posts')
        if cached_posts:
            return cached_posts

        posts = Post.objects.all()
        cache.set('posts', posts, timeout=300)
        return posts
    
def update_average_rating(post_id):
    ratings = Rating.objects.filter(post_id=post_id)
    average_rating = ratings.aggregate(Avg('score'))['score__avg'] if ratings.exists() else 0
    cache.set(f'post:{post_id}:avg_rating', average_rating, timeout=3600)

class RatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            post = get_object_or_404(Post, id=request.data.get('post'))
            if not (0 <= request.data.get('score', -1) <= 5):
                return Response({'error': 'Score must be between 0 and 5'}, status=status.HTTP_400_BAD_REQUEST)
            rating, created = Rating.objects.update_or_create(
                user=user,
                post=post,
                defaults={'score': request.data.get('score')}
            )
            return Response({'message': 'Rating saved successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)