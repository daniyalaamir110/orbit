from cities_light.models import City, Country
from rest_framework.serializers import ModelSerializer


class CountrySerializer(ModelSerializer):
    """Serializer for the Country model"""

    class Meta:
        model = Country
        fields = ["id", "name"]


class CitySerializer(ModelSerializer):
    """Serializer for the City model"""

    class Meta:
        model = City
        fields = ["id", "name"]
