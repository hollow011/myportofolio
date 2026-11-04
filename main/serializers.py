from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Education, Project


def required_text(value):
    cleaned = strip_tags(value).strip()
    if not cleaned:
        raise serializers.ValidationError("This field cannot contain only HTML tags or spaces.")
    return cleaned


class StarredSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and request.user in obj.starred_by.all())

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ProjectSerializer(StarredSerializer):
    tech_stack = serializers.CharField(source="technology", max_length=255)
    project_url = serializers.URLField(source="repository_url", allow_blank=True, required=False, max_length=200)
    validate_title = staticmethod(required_text)
    validate_description = staticmethod(required_text)
    validate_tech_stack = staticmethod(required_text)

    class Meta:
        model = Project
        fields = ("id", "title", "description", "tech_stack", "project_url", "project_image_url",
                  "is_featured", "star_count", "is_starred", "starred_by_names")
        read_only_fields = ("id",)


class EducationSerializer(StarredSerializer):
    degree_display = serializers.CharField(source="get_degree_display", read_only=True)
    validate_institution = staticmethod(required_text)
    validate_field_of_study = staticmethod(required_text)

    def validate_description(self, value):
        return strip_tags(value).strip()

    class Meta:
        model = Education
        fields = ("id", "institution", "degree", "degree_display", "field_of_study", "description",
                  "website", "is_current", "created_at", "star_count", "is_starred", "starred_by_names")
        read_only_fields = ("id", "created_at")
