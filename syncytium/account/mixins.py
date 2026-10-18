from rest_framework.exceptions import NotFound
from rest_framework.permissions import SAFE_METHODS


class MustExistForUsernameAPIMixin:
    """Mixin to check if an object exists for a given username."""

    def get_object(self, create=False):
        """Check if the detail object exists.

        Preconditions:
        - The `model` attribute must be defined in the view.

        Operations:
        - In case of read-only methods, if the object does not exist, raise a 404 error.
        - In case of write methods, if the object does not exist, create it if `create` is `True`.

        Returns:
            `model`: The object for the given username.

        Raises:
        - `NotFound`: If the object does not exist and the method is read-only
        or `create` is `False`.
        """
        username = self.kwargs.get("username")
        try:
            return self.model.objects.get(user__username=username)
        except self.model.DoesNotExist:
            if self.request.method in SAFE_METHODS or not create:
                raise NotFound
            return self.model.objects.create(user_id=self.request.user.id)
