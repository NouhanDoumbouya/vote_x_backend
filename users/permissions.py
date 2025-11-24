from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow only admin users."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "admin"
        )


class IsVoter(BasePermission):
    """Allow authenticated regular (non-admin) voters."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "voter"
        )


class IsAuthenticatedOrGuest(BasePermission):
    """
    Allows:
    - Authenticated users (admin + voter)
    - Unauthenticated guests

    Use in views where guest voting is handled in the serializer.
    """
    def has_permission(self, request, view):
        # Everyone allowed; logic handled elsewhere
        return True
