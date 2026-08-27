from rest_framework.permissions import BasePermission


class IsEntityOwner(BasePermission):
    """
    Permission to prevent one user from
    accessing another user's effects like
    profile or prediction instances.
    """
    def has_permission(self, request, view):
        """
        Checks if a user exists in the request
        and is authenticated or not.
        """
        return (
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Checks the object's user against
        the authenticated user.
        """
        return obj.user == request.user