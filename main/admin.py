from django.contrib import admin

from main.models import Experience, Project


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
