"""Education roles shared by public views, templates, and Django Admin.

Staff status only grants entry to Admin; it is not permission to change
portfolio content. Only membership of the exact Editor group grants editing.
"""


def education_access(user):
    active = user.is_authenticated and user.is_active
    owner = bool(active and user.is_superuser)
    editor = bool(active and user.groups.filter(name="Editor").exists())
    return {
        "can_create_education": owner,
        "can_edit_education": owner or editor,
        "can_delete_education": owner,
    }
