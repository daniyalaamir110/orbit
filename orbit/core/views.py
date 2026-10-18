from cities_light.models import City, Country
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView

from .paginators import CustomLimitOffsetPagination
from .serializers import CitySerializer, CountrySerializer


class CountryListAPIView(ListAPIView):
    """API view to list all countries"""
    serializer_class = CountrySerializer
    search_fields = ["name"]
    filter_backends = [SearchFilter]
    queryset = Country.objects.all()
    pagination_class = CustomLimitOffsetPagination


class CityListAPIView(ListAPIView):
    """API view to list all cities"""
    serializer_class = CitySerializer
    search_fields = ["name"]
    filter_backends = [SearchFilter]
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        country_code = self.kwargs.get("code")
        return City.objects.filter(country__code3=country_code)
