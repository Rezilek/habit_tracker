# habits/permissions.py
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Разрешение на доступ только владельцу объекта."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
