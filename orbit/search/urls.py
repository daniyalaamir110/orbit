from django.urls import path

from .views import SearchAPIView

app_name = "search"

urlpatterns = [
    path("", SearchAPIView.as_view(), name="search"),
]
