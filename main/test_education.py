import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import serializers
from django.test import Client, TestCase
from django.urls import reverse

from main.forms import EducationForm
from main.models import Education, Experience


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


class EducationViewsTest(TestCase):
    def setUp(self):
        self.payload = {
            "institution": "Example University", "degree": "bachelor",
            "field_of_study": "Computer Science", "description": "Study & research.",
        }
        self.education = Education.objects.create(**self.payload, is_current=True)
        self.other = Education.objects.create(
            institution="Other School", degree="secondary", field_of_study="Science"
        )
        self.admin = get_user_model().objects.create_user(username="test-admin", is_staff=True)
        self.list_url = reverse("main:show_education")
        self.add_url = reverse("main:create_education")
        self.edit_url = reverse("main:update_education", args=[self.education.pk])
        self.delete_url = reverse("main:delete_education", args=[self.education.pk])
        self.json_url = reverse("main:get_education_json")

    def test_public_list_and_json_are_accessible(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, self.education.institution)
        self.assertContains(response, "Bachelor&#x27;s degree")
        self.assertContains(response, "Current")
        self.assertContains(response, "Admin sign in")
        self.assertNotContains(response, "Edit education")
        self.assertNotContains(response, 'popovertarget="delete-education-')
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "education.html")
        response = self.client.get(self.json_url)
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["pk"], str(self.education.pk))
        self.assertEqual(data[0]["fields"]["is_current"], True)

    def test_list_consumes_json_response_not_a_separate_queryset(self):
        from django.http import HttpResponse
        encoded = serializers.serialize("json", [self.other])
        with patch("main.views.get_education_json", return_value=HttpResponse(encoded)) as get_json:
            response = self.client.get(self.list_url)
        get_json.assert_called_once()
        self.assertEqual([item.pk for item in response.context["education_list"]], [self.other.pk])

    def test_search_is_case_insensitive_and_trimmed(self):
        for url in (self.list_url, self.json_url):
            with self.subTest(url=url):
                response = self.client.get(url, {"institution": "  eXaMpLe  "})
                self.assertContains(response, "Example University")
                self.assertNotContains(response, self.other.institution)

    def test_empty_search_and_no_matches(self):
        self.assertEqual(len(self.client.get(self.json_url, {"institution": "  "}).json()), 2)
        response = self.client.get(self.list_url, {"institution": "unmatched"})
        self.assertContains(response, "No education matches")
        self.assertEqual(response.context["education_list"], [])
        Education.objects.all().delete()
        self.assertContains(self.client.get(self.list_url), "No education added yet.")
        self.assertEqual(self.client.get(self.json_url).json(), [])

    def test_anonymous_and_nonstaff_cannot_mutate_data(self):
        member = get_user_model().objects.create_user(username="test-member")
        for user in (None, member):
            with self.subTest(user=user):
                if user:
                    self.client.force_login(user)
                for url in (self.add_url, self.edit_url, self.delete_url):
                    response = self.client.post(url, self.payload)
                    self.assertEqual(response.status_code, 302)
                    self.assertTrue(response.url.startswith(reverse("admin:login")))
                self.assertEqual(Education.objects.count(), 2)
                self.education.refresh_from_db()
                self.assertTrue(self.education.is_current)

    def test_inactive_staff_cannot_mutate_data(self):
        self.admin.is_active = False
        self.admin.save()
        self.client.force_login(self.admin)
        for url in (self.add_url, self.edit_url, self.delete_url):
            self.assertEqual(self.client.post(url, self.payload).status_code, 302)
        self.assertEqual(Education.objects.count(), 2)

    def test_admin_create_uses_shared_form_and_redirects(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.add_url)
        self.assertTemplateUsed(response, "education_form.html")
        self.assertTemplateUsed(response, "components/form_fields.html")
        self.assertFalse(response.context["form"].is_bound)
        response = self.client.post(self.add_url, self.payload, follow=True)
        self.assertRedirects(response, self.list_url)
        self.assertContains(response, "Education added successfully!")
        self.assertEqual(Education.objects.count(), 3)

    def test_admin_edit_is_prefilled_and_does_not_create_duplicate(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.edit_url)
        self.assertContains(response, 'value="Example University"')
        self.assertContains(response, "Save changes")
        self.assertEqual(response.context["form"].instance.pk, self.education.pk)
        created_at = self.education.created_at
        response = self.client.post(self.edit_url, {**self.payload, "institution": "Renamed School"}, follow=True)
        self.assertRedirects(response, self.list_url)
        self.assertContains(response, "Education updated successfully!")
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Renamed School")
        self.assertEqual(self.education.created_at, created_at)
        self.assertFalse(self.education.is_current)
        self.assertEqual(Education.objects.count(), 2)
        self.other.refresh_from_db()
        self.assertEqual(self.other.institution, "Other School")

    def test_invalid_create_and_update_keep_input_without_saving(self):
        self.client.force_login(self.admin)
        for url in (self.add_url, self.edit_url):
            with self.subTest(url=url):
                response = self.client.post(url, {**self.payload, "institution": "Attempted edit", "website": "not-a-url"})
                self.assertEqual(response.status_code, 200)
                self.assertIn("website", response.context["form"].errors)
                self.assertContains(response, 'value="Attempted edit"')
                self.assertEqual(Education.objects.count(), 2)
                self.education.refresh_from_db()
                self.assertEqual(self.education.institution, "Example University")

    def test_empty_post_is_bound_and_rejected(self):
        self.client.force_login(self.admin)
        for url in (self.add_url, self.edit_url):
            response = self.client.post(url, {})
            self.assertTrue(response.context["form"].is_bound)
            self.assertEqual(set(response.context["form"].errors), {"institution", "degree", "field_of_study"})
        self.assertEqual(Education.objects.count(), 2)

    def test_post_cannot_override_id_or_timestamp(self):
        self.client.force_login(self.admin)
        original_created = self.education.created_at
        response = self.client.post(self.edit_url, {
            **self.payload, "id": str(self.other.pk), "created_at": "2000-01-01T00:00:00Z",
        })
        self.assertRedirects(response, self.list_url)
        self.education.refresh_from_db()
        self.assertEqual(self.education.created_at, original_created)
        self.other.refresh_from_db()
        self.assertEqual(self.other.institution, "Other School")

    def test_delete_requires_post_and_removes_only_target(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(self.delete_url).status_code, 405)
        self.assertTrue(Education.objects.filter(pk=self.education.pk).exists())
        response = self.client.post(self.delete_url, follow=True)
        self.assertRedirects(response, self.list_url)
        self.assertContains(response, "Education deleted successfully!")
        self.assertFalse(Education.objects.filter(pk=self.education.pk).exists())
        self.assertTrue(Education.objects.filter(pk=self.other.pk).exists())

    def test_unknown_uuid_returns_404(self):
        self.client.force_login(self.admin)
        for name in ("update_education", "delete_education"):
            response = self.client.post(reverse(f"main:{name}", args=[uuid.uuid4()]), self.payload)
            self.assertEqual(response.status_code, 404)

    def test_csrf_is_required_even_for_admin(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        for url in (self.add_url, self.edit_url, self.delete_url):
            self.assertEqual(client.post(url, self.payload).status_code, 403)
        client.get(self.add_url)
        token = client.cookies["csrftoken"].value
        payload = {**self.payload, "csrfmiddlewaretoken": token}
        self.assertEqual(client.post(self.edit_url, payload, HTTP_ORIGIN="https://attacker.invalid").status_code, 403)
        for url in (self.add_url, self.edit_url, self.delete_url):
            response = client.post(url, payload, HTTP_ORIGIN="https://mohammad-adzka-myportofolio.pws.cs.ui.ac.id")
            self.assertRedirects(response, self.list_url)

    def test_admin_sees_unique_delete_confirmations(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.list_url)
        self.assertContains(response, "Add education")
        for education in (self.education, self.other):
            self.assertContains(response, f'id="delete-education-{education.pk}"', count=1)
        self.assertContains(response, 'name="csrfmiddlewaretoken"', count=2)

    def test_html_is_escaped(self):
        self.education.institution = '<script>alert("test")</script>'
        self.education.save()
        response = self.client.get(self.list_url)
        self.assertNotContains(response, "<script>")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(self.client.get(self.list_url, {"institution": "<script>"}), "<script>")

    def test_read_endpoints_reject_post_and_form_rejects_put(self):
        self.client.force_login(self.admin)
        for url in (self.list_url, self.json_url, reverse("main:get_experience_json")):
            self.assertEqual(self.client.post(url).status_code, 405)
        for url in (self.add_url, self.edit_url):
            self.assertEqual(self.client.put(url).status_code, 405)

    def test_experience_json_round_trip_and_empty_state(self):
        url = reverse("main:get_experience_json")
        self.assertEqual(self.client.get(url).json(), [])
        experience = Experience.objects.create(title="Example role", description="Test only", category="part-time")
        response = self.client.get(url)
        self.assertEqual(response["Content-Type"], "application/json")
        objects = list(serializers.deserialize("json", response.content.decode()))
        self.assertEqual(objects[0].object.pk, experience.pk)

    def test_every_page_uses_base_template_and_one_document(self):
        self.client.force_login(self.admin)
        urls = ["/", "/experience/", "/projects/", "/projects/add/", self.list_url, self.add_url, self.edit_url]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "base.html")
                self.assertContains(response, "<!doctype html>", count=1)
                self.assertContains(response, 'href="/education/"')
