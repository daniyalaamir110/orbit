from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import CurrentUserRetrieveAPIView, GoogleLoginAPIView

app_name = "authentication"

password_reset = include("django_rest_passwordreset.urls", namespace="password_reset")

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("login/google/", GoogleLoginAPIView.as_view(), name="google"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("verify/", TokenVerifyView.as_view(), name="verify"),
    path("me/", CurrentUserRetrieveAPIView.as_view(), name="me"),
    path("password_reset/", password_reset),
]
