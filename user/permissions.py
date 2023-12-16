from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
        Only admin users can create/update/delete books
        All users (even those not authenticated) able only to read/retrieve
    """
    def has_permission(self, request, view):
        return bool(
            (request.user and request.user.is_staff)
            or
            request.method in SAFE_METHODS
        )


class IsAdminOrIfAuthenticatedReadAndCreateOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method in ("GET", "POST", "HEAD", "OPTIONS")
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):

    def has_permission(self, request, view):

        return (
            (
                request.method in SAFE_METHODS
                and request.user.is_authenticated
            )
            or (request.user.is_authenticated and request.user.is_staff)
        )