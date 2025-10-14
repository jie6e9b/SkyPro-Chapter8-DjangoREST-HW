from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.groups.filter(name="Moderators").exists()
        return False

    def has_object_permission(self, request, view, obj):
        # Mirror the same logic for object-level checks so that
        # negation (~IsModerator) works correctly in object permissions.
        return self.has_permission(request, view)


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
