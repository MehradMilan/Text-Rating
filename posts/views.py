from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, PostAverageRating, Rating
from .serializers import PostSerializer, RatingSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from .pagination import CustomPagination
from django.db.models import Avg
from .kafka_producers import send_rating_event
import json
import time

ANOMALY_THRESHOLD = 0.6
SUSPICIOUS_BUFFER_SIZE = 50

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

def check_for_anomalies(post_id):
    redis_client = cache.client.get_client()

    ratings = redis_client.zrangebyscore(f'post:{post_id}:rating_buffer', '-inf', '+inf')
    if not ratings:
        return

    scores = [json.loads(rating)['score'] for rating in ratings]

    score_count = {score: scores.count(score) for score in set(scores)}

    total_ratings = len(scores)
    for score, count in score_count.items():
        if count / total_ratings > ANOMALY_THRESHOLD:
            print(f"Anomaly detected: {count}/{total_ratings} ratings are {score}. Clearing buffer.")
            redis_client.delete(f'post:{post_id}:rating_buffer')
            return


class RatingView(APIView):
    permission_classes = [IsAuthenticated]

    def add_rating_to_buffer(self, post_id, user_id, score):
        redis_client = cache.client.get_client()
        current_time = time.time()
        rating_data = json.dumps({
            "user_id": user_id,
            "score": score,
            "timestamp": current_time
        })

        redis_client.zadd(f'post:{post_id}:rating_buffer', {rating_data: current_time})

        buffer_size = redis_client.zcard(f'post:{post_id}:rating_buffer')
        if buffer_size > SUSPICIOUS_BUFFER_SIZE:
            print(f"Buffer for post {post_id} is suspicious. Triggering anomaly detection.")
            check_for_anomalies(post_id)

    def post(self, request):
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            post = get_object_or_404(Post, id=request.data.get('post'))

            score = request.data.get('score', -1)
            if not (0 <= score <= 5):
                return Response({'error': 'Score must be between 0 and 5'}, status=status.HTTP_400_BAD_REQUEST)

            rating, created = Rating.objects.get_or_create(
                user=user, post=post, defaults={'score': score}
            )
            
            if not created:
                rating.score = score
                rating.save()
            
            self.add_rating_to_buffer(post.id, user.id, request.data.get('score'))

            send_rating_event(post.id, request.data.get('score'), user.id)

            return Response({'message': 'Rating buffered successfully'}, status=status.HTTP_200_OK)
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
    
class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            PostAverageRating.objects.create(post=post)
            return Response({'message': 'Post created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)