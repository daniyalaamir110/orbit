from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCurrentUserPermission(BasePermission):
    """Permission class to check if the current user is the same as the user
    in the URL, otherwise, raise `PermissionDenied`.
    """
    def has_permission(self, request, view):
        username = view.kwargs.get("username")
        current_user = request.user
        is_current_user = current_user.username == username
        if is_current_user:
            return True
        raise PermissionDenied("You do not have permission to access this resource.")


class IsCurrentUserOrReadOnlyPermission(IsCurrentUserPermission):
    """Permission class to check if the current user is the same as the user
    in the URL. If the user is not the same, only allow read-only methods.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)

