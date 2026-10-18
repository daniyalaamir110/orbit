from rest_framework import serializers

from feed.serializers import AuthorSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializes a notification with its actor and a post snippet."""

    actor = AuthorSerializer(read_only=True)
    verb_display = serializers.CharField(source="get_verb_display", read_only=True)
    post = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id", "actor", "verb", "verb_display", "post", "is_read", "created",
        ]

    def get_post(self, obj):
        if not obj.post_id:
            return None
        content = obj.post.content
        return {
            "id": obj.post_id,
            "excerpt": content[:80] + ("…" if len(content) > 80 else ""),
        }
