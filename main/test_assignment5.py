from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

from main.forms import EducationForm
from main.models import Education


class EducationAjaxTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.owner = users.create_user("ajax-owner", is_superuser=True)
        cls.editor = users.create_user("ajax-editor")
        cls.editor.groups.add(Group.objects.get_or_create(name="Editor")[0])
        cls.member = users.create_user("ajax-member", email="private@example.invalid")
        cls.staff = users.create_user("ajax-staff", is_staff=True)
        cls.url = reverse("main:create_education_ajax")
        cls.json_url = reverse("main:get_education_json")
        cls.list_url = reverse("main:show_education")
        cls.payload = {"institution": "Example University", "degree": "bachelor",
                       "field_of_study": "Computer Science", "description": "Unique fixture text."}

    def test_only_owner_can_add_and_denial_is_json_without_redirect(self):
        for user in (None, self.member, self.editor, self.staff):
            self.client.logout()
            if user:
                self.client.force_login(user)
            response = self.client.post(self.url, {
                **self.payload, "is_superuser": "true", "can_create_education": "true",
            })
            self.assertEqual(response.status_code, 403)
            self.assertIn("message", response.json())
            self.assertNotIn("Location", response)
        self.assertEqual(Education.objects.count(), 0)

    def test_inactive_owner_is_denied(self):
        self.owner.is_active = False
        self.owner.save()
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 403)
        self.assertEqual(Education.objects.count(), 0)

    def test_creation_returns_201_uuid_and_cleaned_fields(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, {
            **self.payload, "institution": "  <b>Example</b> University ",
            "field_of_study": "<em>Computer Science</em>", "description": "<p>Text</p>",
            "website": "https://example.edu", "is_current": "on",
            "starred_by": [self.member.pk], "created_at": "2000-01-01",
        })
        self.assertEqual(response.status_code, 201)
        entry = Education.objects.get(pk=response.json()["pk"])
        self.assertEqual(entry.institution, "Example University")
        self.assertEqual(entry.field_of_study, "Computer Science")
        self.assertEqual(entry.description, "Text")
        self.assertTrue(entry.is_current)
        self.assertEqual(entry.website, "https://example.edu")
        self.assertEqual(entry.starred_by.count(), 0)
        self.assertNotEqual(entry.created_at.year, 2000)

    def test_validation_failures_do_not_save(self):
        self.client.force_login(self.owner)
        for field, value in (
            ("institution", " "), ("institution", '<img src=x onerror="alert(1)">'),
            ("field_of_study", "<br>"), ("institution", "a" * 256),
            ("degree", "<b>bachelor</b>"), ("degree", "invented"),
            ("website", "javascript:alert(1)"), ("website", "data:text/html,test"),
        ):
            with self.subTest(field=field, value=value):
                response = self.client.post(self.url, {**self.payload, field: value})
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json()["errors"])
        self.assertEqual(Education.objects.count(), 0)

    def test_optional_description_can_be_empty_after_cleaning(self):
        form = EducationForm({**self.payload, "description": "<br>"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().description, "")

    def test_legacy_create_and_editor_update_use_same_cleaning(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("main:create_education"), {
            **self.payload, "institution": "<br>",
        })
        self.assertIn("institution", response.context["form"].errors)
        entry = Education.objects.create(**self.payload)
        self.client.force_login(self.editor)
        self.client.post(reverse("main:update_education", args=[entry.pk]), {
            **self.payload, "institution": "<b>Edited</b>",
        })
        entry.refresh_from_db()
        self.assertEqual(entry.institution, "Edited")
        self.assertEqual(Education.objects.count(), 1)

    def test_post_only(self):
        self.client.force_login(self.owner)
        for method in ("get", "put", "patch", "delete"):
            self.assertEqual(getattr(self.client, method)(self.url).status_code, 405)

    def test_csrf_and_origin_checks_apply_to_ajax(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(self.url, self.payload).status_code, 403)
        client.get(self.list_url)
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.url, self.payload, HTTP_X_CSRFTOKEN=token,
                                    HTTP_ORIGIN="https://attacker.invalid").status_code, 403)
        self.assertEqual(client.post(self.url, self.payload, HTTP_X_CSRFTOKEN=token).status_code, 201)
        self.assertEqual(client.post(self.url, {
            **self.payload, "csrfmiddlewaretoken": token,
        }).status_code, 201)

    def test_json_is_personalized_public_filtered_and_private_cache(self):
        entry = Education.objects.create(**self.payload)
        entry.starred_by.add(self.member)
        for user in (None, self.member, self.editor, self.staff, self.owner):
            self.client.logout()
            if user:
                self.client.force_login(user)
            response = self.client.get(self.json_url, {"institution": "  eXaMpLe  "})
            fields = response.json()[0]["fields"]
            self.assertEqual(fields["star_count"], 1)
            self.assertEqual(fields["is_starred"], user == self.member)
            self.assertEqual(fields["degree_display"], "Bachelor's degree")
            self.assertEqual(fields["starred_by_names"], self.member.username)
            self.assertNotContains(response, self.member.email)
            self.assertNotIn("password", fields)
            self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(self.client.get(self.json_url, {"institution": "absent"}).json(), [])

    def test_shell_does_not_embed_data_and_forms_match_roles(self):
        Education.objects.create(**self.payload)
        for user in (None, self.member, self.editor, self.staff, self.owner):
            self.client.logout()
            if user:
                self.client.force_login(user)
            response = self.client.get(self.list_url, {"institution": "  Example  "})
            self.assertContains(response, 'value="Example"')
            self.assertContains(response, 'id="education-grid"')
            self.assertContains(response, "js/education.js")
            self.assertContains(response, "js/toast.js")
            self.assertNotIn("education_list", response.context)
            self.assertNotContains(response, self.payload["description"])
            self.assertEqual(b'id="education-form"' in response.content, user == self.owner)
            self.assertEqual(response.context["can_edit_education"], user in (self.editor, self.owner))

    def test_json_star_prefetch_is_constant_queries(self):
        for i in range(8):
            entry = Education.objects.create(**{**self.payload, "institution": f"School {i}"})
            entry.starred_by.add(self.member)
        # Anonymous requests: one query for rows and one for all related users.
        with self.assertNumQueries(2):
            response = self.client.get(self.json_url)
        self.assertEqual(len(response.json()), 8)

    def test_stored_html_remains_data_in_json(self):
        entry = Education.objects.create(**{
            **self.payload, "institution": '<img src=x onerror="alert(1)">',
        })
        response = self.client.get(self.json_url)
        self.assertEqual(response.json()[0]["fields"]["institution"], entry.institution)
        self.assertEqual(response["Content-Type"], "application/json")
