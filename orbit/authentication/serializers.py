from rest_framework import serializers


class GoogleLoginInputSerializer(serializers.Serializer):
    """Serializer for the Google login input"""

    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
