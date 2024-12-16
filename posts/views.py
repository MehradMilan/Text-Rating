from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Rating
from .serializers import PostSerializer, RatingSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from .pagination import CustomPagination

class PostList(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = CustomPagination

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
