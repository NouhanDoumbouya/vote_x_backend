from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Allow only admin users."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsVoter(BasePermission):
    """Allow authenticated non-admin (regular voter) users."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "voter"
        )


class IsAuthenticatedOrGuest(BasePermission):
    """
    Allow authenticated users OR allow guests for certain endpoints
    (future: IP-based guest voting).
    """

    def has_permission(self, request, view):
        return True  # allowed for now (we'll refine later)
