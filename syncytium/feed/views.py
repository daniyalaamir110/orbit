from django.db.models import Count, Exists, OuterRef
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.paginators import CustomLimitOffsetPagination

from .models import Comment, Like, Post
from .permissions import IsAuthorOrReadOnly
from .serializers import CommentSerializer, PostSerializer


class PostViewSet(ModelViewSet):
    """CRUD for feed posts, plus like/unlike and comment sub-resources."""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    http_method_names = ["get", "post", "patch", "delete"]

    def get_permissions(self):
        # Only editing or deleting a post is restricted to its author.
        # Liking and commenting are open to any authenticated user.
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.select_related("author").annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
        )
        if user.is_authenticated:
            queryset = queryset.annotate(
                liked_by_user=Exists(
                    Like.objects.filter(post=OuterRef("pk"), user=user)
                )
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        """Toggle the current user's like on a post."""
        post = self.get_object()
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
        serializer = self.get_serializer(self.get_queryset().get(pk=post.pk))
        return Response(
            {"liked": created, "post": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        """List comments on a post, or add a new one."""
        post = self.get_object()
        if request.method == "POST":
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        queryset = post.comments.select_related("author")
        page = self.paginate_queryset(queryset)
        serializer = CommentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
