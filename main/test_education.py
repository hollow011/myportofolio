import uuid

from django.test import TestCase

from main.forms import EducationForm
from main.models import Education


class EducationFormTest(TestCase):
    def setUp(self):
        self.payload = {
            "institution": "Example University",
            "degree": "bachelor",
            "field_of_study": "Computer Science",
        }

    def test_form_exposes_every_editable_field(self):
        editable = {field.name for field in Education._meta.fields if field.editable}
        self.assertEqual(set(EducationForm().fields), editable)
        self.assertNotIn("id", editable)
        self.assertNotIn("created_at", editable)

    def test_valid_form_saves_optional_defaults(self):
        form = EducationForm(self.payload)
        self.assertTrue(form.is_valid(), form.errors)
        education = form.save()
        self.assertIsInstance(education.pk, uuid.UUID)
        self.assertEqual(education.description, "")
        self.assertEqual(education.website, "")
        self.assertFalse(education.is_current)
        self.assertEqual(str(education), "Example University - Computer Science")

    def test_optional_fields_are_saved(self):
        form = EducationForm({**self.payload, "description": "A test record.",
                              "website": "https://example.edu", "is_current": "on"})
        self.assertTrue(form.is_valid(), form.errors)
        education = form.save()
        self.assertTrue(education.is_current)
        self.assertEqual(education.website, "https://example.edu")

    def test_empty_form_reports_required_fields(self):
        form = EducationForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors), {"institution", "degree", "field_of_study"})

    def test_invalid_choice_url_and_length_are_rejected(self):
        for field, value in (("degree", "invalid"), ("website", "javascript:alert(1)"),
                             ("institution", "x" * 256), ("field_of_study", "x" * 256)):
            with self.subTest(field=field):
                form = EducationForm({**self.payload, field: value})
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_instance_update_keeps_uuid_timestamp_and_row_count(self):
        original = Education.objects.create(**self.payload, is_current=True)
        form = EducationForm({**self.payload, "institution": "Updated University"}, instance=original)
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        self.assertEqual(updated.pk, original.pk)
        self.assertEqual(updated.created_at, original.created_at)
        self.assertFalse(updated.is_current)
        self.assertEqual(Education.objects.count(), 1)

    def test_current_education_is_ordered_first(self):
        current = Education.objects.create(**self.payload, is_current=True)
        past = Education.objects.create(**self.payload)
        self.assertEqual(list(Education.objects.all()), [current, past])
