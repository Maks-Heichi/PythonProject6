"""Права доступа для пользователей, курсов и уроков."""

from rest_framework.permissions import BasePermission


class IsModer(BasePermission):
    """Проверяет, является ли пользователь модератором."""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()

    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
