from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import (
    validate_password as validate_password_django,
)
from rest_framework import serializers

from core.serializers import CitySerializer, CountrySerializer
from core.utils import validate_country_and_city

from .models import (
    UserAddress, UserEducation, UserProfile, UserWorkExperience
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User create serializer"""

    password = serializers.CharField(
        write_only=True, required=True, min_length=8, max_length=20
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "first_name", "last_name", "full_name", "username", 
            "email", "password"
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "email": {"required": True},
            "full_name": {"read_only": True}
        }

    def validate_password(self, password):
        validate_password_django(password)
        return password

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class SuggestedUserSerializer(serializers.ModelSerializer):
    """Compact user representation for friend suggestions."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ChangeEmailSerializer(serializers.ModelSerializer):
    """Change email serializer"""

    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email"]
        extra_kwargs = {"email": {"required": True}}

    def validate_email(self, email):
        user = self.context["request"].user
        if user.email == email:
            raise serializers.ValidationError("Email is already the same.")
        return email


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""

    class Meta:
        model = UserProfile
        fields = ["id", "user", "bio"]
        extra_kwargs = {"user": {"read_only": True}}


class UserAddressSerializer(serializers.ModelSerializer):
    """User address serializer"""

    class Meta:
        model = UserAddress
        fields = ["id", "user", "country", "city"]
        extra_kwargs = {"user": {"read_only": True}}

    def validate(self, attrs):
        attrs = super().validate(attrs)
        city = attrs.get("city")
        country = attrs.get("country")
        if city:
            country, city = validate_country_and_city(country, city)
        attrs["country"] = country
        attrs["city"] = city
        return attrs
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.city:
            data['city'] = CitySerializer(instance.city).data
        if instance.country:
            data['country'] = CountrySerializer(instance.country).data
        return data


class UserEducationSerializer(serializers.ModelSerializer):
    """User education serializer"""

    class Meta:
        model = UserEducation
        fields = [
            "id", "user", "school", "degree", "field_of_study", 
            "start_date", "end_date", "description"
        ]
        extra_kwargs = {"user": {"read_only": True}}


class UserWorkExperienceSerializer(serializers.ModelSerializer):
    """User work experience serializer"""

    class Meta:
        model = UserWorkExperience
        fields = [
            "id", "user", "company", "position", "start_date", 
            "end_date", "description"
        ]
        extra_kwargs = {"user": {"read_only": True}}
