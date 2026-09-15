from django import forms

from main.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "technology",
            "repository_url",
            "project_image_url",
            "is_featured",
        ]
        labels = {
            "title": "Project name",
            "description": "Description",
            "technology": "Technologies used",
            "repository_url": "Source code URL (optional)",
            "project_image_url": "Image URL (optional)",
            "is_featured": "Feature this project",
        }
        help_texts = {
            "project_image_url": "Use a publicly accessible image URL, not a file upload.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Portfolio Website"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "technology": forms.TextInput(attrs={"placeholder": "Django, Python, HTML, CSS"}),
            "repository_url": forms.URLInput(attrs={"placeholder": "https://github.com/..."}),
            "project_image_url": forms.URLInput(attrs={"placeholder": "https://example.com/project.png"}),
        }
