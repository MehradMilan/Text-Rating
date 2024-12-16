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
from .kafka_producers import send_rating_event

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
    
    def get_serializer_context(self):
        return {'request': self.request}
    
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

            send_rating_event(post.id, request.data.get('score'), user.id)

            update_average_rating(post.id)

            return Response({'message': 'Rating saved successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AnalyticsView(APIView):
    def get(self, request):
        most_rated = cache.client.get_client().zrevrange('most_rated_posts', 0, 4, withscores=True)

        top_rated = []
        for key in most_rated:
            post_id = key[0].decode('utf-8').split(':')[1]
            avg_rating = cache.get(f'post:{post_id}:avg_rating', 0)
            top_rated.append({'post_id': post_id, 'average_rating': avg_rating})

        return Response({
            'most_rated': most_rated,
            'top_rated': top_rated
        })