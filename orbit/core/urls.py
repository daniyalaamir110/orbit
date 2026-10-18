from django.urls import path, re_path

from .views import CityListAPIView, CountryListAPIView

urlpatterns = [
    path("country/", CountryListAPIView.as_view(), name="countries"),
    re_path(
        r"^country/(?P<code>[A-Z]{3})/cities/$",
        CityListAPIView.as_view(),
        name="cities",
    ),
]
