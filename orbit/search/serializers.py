from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSearchSerializer(serializers.ModelSerializer):
    """Compact user representation for search results."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
