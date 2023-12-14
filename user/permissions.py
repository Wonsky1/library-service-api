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
