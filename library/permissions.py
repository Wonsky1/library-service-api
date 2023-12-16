from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True

        return False
