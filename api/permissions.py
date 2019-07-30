from rest_framework.permissions import BasePermission

from main.models import User


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return getattr(request.user, "is_staff", False) or getattr(request.user, "is_superuser", False) \
                or getattr(request.user, "is_admin", False)


class IsTeacher(BasePermission):

    def has_permission(self, request, view):
        return request.user and getattr(request.user, "type", "") == User.TEACHER
