from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Comment, Like, Post

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """Compact author representation embedded in posts and comments."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for post comments."""
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "content", "created"]
        extra_kwargs = {"post": {"read_only": True}}


class PostSerializer(serializers.ModelSerializer):
    """Serializer for feed posts, with engagement counts and the
    current user's like state.
    """
    author = AuthorSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "author", "content", "created", "modified",
            "like_count", "comment_count", "liked",
        ]

    def _request_user(self):
        request = self.context.get("request")
        return getattr(request, "user", None)

    def get_like_count(self, obj):
        # Uses the annotated value when present, else falls back to a query.
        return getattr(obj, "like_count", None) or obj.likes.count()

    def get_comment_count(self, obj):
        return getattr(obj, "comment_count", None) or obj.comments.count()

    def get_liked(self, obj):
        annotated = getattr(obj, "liked_by_user", None)
        if annotated is not None:
            return bool(annotated)
        user = self._request_user()
        if not user or not user.is_authenticated:
            return False
        return Like.objects.filter(post=obj, user=user).exists()
