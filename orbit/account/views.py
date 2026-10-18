from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.models import RegistrationMethod
from notifications.models import Notification

from .mixins import MustExistForUsernameAPIMixin
from .models import (
    Follow, UserAddress, UserEducation, UserEmailStatus, UserProfile,
    UserWorkExperience,
)
from .permissions import (
    IsCurrentUserOrReadOnlyPermission, IsCurrentUserPermission,
)
from .serializers import (
    ChangeEmailSerializer, SuggestedUserSerializer, UserAddressSerializer,
    UserEducationSerializer, UserProfileSerializer, UserSerializer,
    UserWorkExperienceSerializer,
)
from .tasks import send_email_verification_link_email, send_registration_email

User = get_user_model()


class SuggestionsAPIView(ListAPIView):
    """Suggest users to follow: excludes self and already-followed, random order."""
    serializer_class = SuggestedUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        followed = Follow.objects.filter(follower=user).values_list(
            "following_id", flat=True
        )
        limit = min(int(self.request.query_params.get("limit", 5) or 5), 20)
        return (
            User.objects.exclude(id=user.id)
            .exclude(id__in=followed)
            .order_by("?")[:limit]
        )


class FollowToggleAPIView(APIView):
    """Toggle following the user named in the URL. Returns {following: bool}."""
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=HTTP_400_BAD_REQUEST,
            )
        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=target
        )
        if created:
            Notification.push(
                recipient=target,
                actor=request.user,
                verb=Notification.Verb.FOLLOW,
            )
            return Response({"following": True}, status=HTTP_200_OK)
        follow.delete()
        Notification.objects.filter(
            recipient=target, actor=request.user, verb=Notification.Verb.FOLLOW
        ).delete()
        return Response({"following": False}, status=HTTP_200_OK)


class UserCreateAPIView(CreateAPIView):
    """API view to create a new user"""
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        password = serializer.validated_data.pop("password")
        serializer.save()
        user = serializer.instance
        user.set_password(password)
        user.save()
        # send_registration_email.delay(user.id)
        send_registration_email(user.id)
        # send_email_verification_link_email.delay(user.id, is_new=True)
        send_email_verification_link_email(user.id, is_new=True)
        return user


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCurrentUserPermission])
def get_email_token(request, username):
    """API view to get email token"""
    user = User.objects.filter(username=username).select_related("email_status").first()
    if not user:
        return Response({"detail": "User not found."}, status=HTTP_404_NOT_FOUND)
    if user.email_status.is_verified:
        return Response(
            {"detail": "Email is already verified."}, status=HTTP_400_BAD_REQUEST
        )
    # send_email_verification_link_email.delay(user.id)
    send_email_verification_link_email(user.id)
    return Response(
        {"detail": "Email verification link will be sent to you soon."},
        status=HTTP_200_OK,
    )


@api_view(["GET"])
def verify_email(request, token):
    """API view to verify email"""
    email_status = UserEmailStatus.objects.filter(verification_token=token).first()
    if not email_status:
        detail = "Invalid link"
    elif email_status.is_verified:
        detail = "Email is already verified."
    elif not email_status.is_token_valid:
        detail = "Link expired. Please generate a new link."
    else:
        detail = "Email verified successfully."
        email_status.is_verified = True
        email_status.save()
    return render(request, "account/verify_email.html", {"detail": detail})


class UserChangeEmailAPIView(UpdateAPIView):
    """API view to change user email."""
    serializer_class = ChangeEmailSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsCurrentUserPermission]
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        user = serializer.instance
        if user.registration_method == RegistrationMethod.GOOGLE:
            return Response(
                {"detail": "Email cannot be changed for Google registered users."},
                status=HTTP_400_BAD_REQUEST,
            )
        super().perform_update(serializer)
        # send_email_verification_link_email.delay(user.id)
        send_email_verification_link_email(user.id)
        return user


class UserProfileAPIView(RetrieveUpdateAPIView):
    """API view to manage user profile"""
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsCurrentUserOrReadOnlyPermission,
    ]
    http_method_names = ["get", "patch"]
    model = UserProfile

    def get_object(self):
        return MustExistForUsernameAPIMixin.get_object(self, create=True)


class UserAddressAPIView(RetrieveUpdateAPIView):
    """API view to manage user address"""
    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsCurrentUserOrReadOnlyPermission,
    ]
    http_method_names = ["get", "patch"]
    model = UserAddress

    def get_object(self):
        return MustExistForUsernameAPIMixin.get_object(self, create=True)


class UserEducationViewSet(ModelViewSet):
    """API view to manage user education"""
    serializer_class = UserEducationSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsCurrentUserOrReadOnlyPermission,
    ]
    http_method_names = ["get", "post", "patch", "delete"]
    model = UserEducation

    def get_queryset(self):
        username = self.kwargs.get("username")
        return self.model.objects.filter(user__username=username)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserWorkExperienceViewSet(ModelViewSet):
    """API view to manage user work experience"""

    serializer_class = UserWorkExperienceSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsCurrentUserOrReadOnlyPermission,
    ]
    http_method_names = ["get", "post", "patch", "delete"]
    model = UserWorkExperience

    def get_queryset(self):
        username = self.kwargs.get("username")
        return self.model.objects.filter(user__username=username)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
