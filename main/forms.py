from django import forms
from django.utils.html import strip_tags

from main.models import Education, Project


class ProjectForm(forms.ModelForm):
    def _clean_text(self, field):
        value = strip_tags(self.cleaned_data[field]).strip()
        if not value:
            raise forms.ValidationError("This field cannot contain only HTML tags or spaces.")
        return value

    def clean_title(self):
        return self._clean_text("title")

    def clean_description(self):
        return self._clean_text("description")

    def clean_technology(self):
        return self._clean_text("technology")

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


class EducationForm(forms.ModelForm):
    """Expose editable education data, never the UUID or creation timestamp."""

    def _clean_text(self, field):
        # Defense in depth only: rendering must still escape old/stored data.
        value = strip_tags(self.cleaned_data[field]).strip()
        if self.fields[field].required and not value:
            raise forms.ValidationError("This field cannot contain only HTML tags or spaces.")
        return value

    def clean_institution(self):
        return self._clean_text("institution")

    def clean_field_of_study(self):
        return self._clean_text("field_of_study")

    def clean_description(self):
        return self._clean_text("description")

    class Meta:
        model = Education
        fields = [
            "institution", "degree", "field_of_study", "description",
            "website", "is_current",
        ]
        labels = {
            "institution": "Institution",
            "degree": "Qualification level",
            "field_of_study": "Field of study",
            "description": "Description (optional)",
            "website": "Institution website (optional)",
            "is_current": "Currently studying here",
        }
        widgets = {
            "institution": forms.TextInput(attrs={"placeholder": "Institution name"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "website": forms.URLInput(attrs={"placeholder": "https://example.edu"}),
        }
