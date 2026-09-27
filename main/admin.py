from django.contrib import admin

from main.models import Education, Experience, Project
from main.permissions import education_access


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "started_at", "ended_at")
    list_filter = ("category",)
    search_fields = ("title", "description")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "technology", "is_featured", "created_at")
    list_filter = ("is_featured",)
    search_fields = ("title", "description", "technology")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("institution", "degree", "field_of_study", "is_current")
    list_filter = ("degree", "is_current")
    search_fields = ("institution", "field_of_study", "description")

    def has_view_permission(self, request, obj=None):
        return education_access(request.user)["can_edit_education"]

    def has_change_permission(self, request, obj=None):
        return education_access(request.user)["can_edit_education"]

    def has_add_permission(self, request):
        return education_access(request.user)["can_create_education"]

    def has_delete_permission(self, request, obj=None):
        return education_access(request.user)["can_delete_education"]

    def has_module_permission(self, request):
        return self.has_view_permission(request)
