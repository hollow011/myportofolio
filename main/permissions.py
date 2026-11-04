"""Education roles shared by public views, templates, and Django Admin.

Staff status only grants entry to Admin; it is not permission to change
portfolio content. Only membership of the exact Editor group grants editing.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


def education_access(user):
    active = user.is_authenticated and user.is_active
    owner = bool(active and user.is_superuser)
    editor = bool(active and user.groups.filter(name="Editor").exists())
    return {
        "can_create_education": owner,
        "can_edit_education": owner or editor,
        "can_delete_education": owner,
    }


class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_active and request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        key = "can_edit_education" if request.method in ("PUT", "PATCH") else "can_create_education"
        return education_access(request.user)[key]
