from rest_framework import permissions


class IsReadOnly(permissions.BasePermission):
    """Read only permission."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsModeratorOrIsAdminOrSuperUser(permissions.BasePermission):
    """Moderator permission."""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            user = request.user
            return user.is_moderator or user.is_admin or user.is_superuser
        return False


class IsAdministrator(permissions.BasePermission):
    """Administrator permission."""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            user = request.user
            return user.is_admin or user.is_superuser
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Author, moderator & admins can edit or delete object permission."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.user.is_admin or request.user.is_moderator
                or request.user.is_superuser or obj.author == request.user)
