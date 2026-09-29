from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from main.forms import ProjectForm
from main.models import Project


class Tutorial5Test(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user("ajax-owner", is_superuser=True)
        self.member = get_user_model().objects.create_user("ajax-member")
        self.staff = get_user_model().objects.create_user("ajax-staff", is_staff=True)
        self.url = reverse("main:create_project_ajax")
        self.payload = {"title": "New project", "description": "Unique project fixture description.", "technology": "Django"}

    def test_anonymous_member_and_staff_get_json_403(self):
        for user in (None, self.member, self.staff):
            self.client.logout()
            if user:
                self.client.force_login(user)
            response = self.client.post(self.url, self.payload)
            self.assertEqual(response.status_code, 403)
            self.assertIn("message", response.json())
        self.assertEqual(Project.objects.count(), 0)

    def test_post_only(self):
        self.client.force_login(self.owner)
        for method in ("get", "put", "delete", "patch"):
            self.assertEqual(getattr(self.client, method)(self.url).status_code, 405)

    def test_create_uses_form_and_ignores_forged_star_fields(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, {
            **self.payload, "title": "  Hello <b>world</b>  ",
            "description": "<p>Text</p>", "technology": "<b>Django</b>",
            "is_featured": "on", "starred_by": [self.member.pk],
        })
        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(pk=response.json()["pk"])
        self.assertEqual(project.title, "Hello world")
        self.assertEqual(project.description, "Text")
        self.assertEqual(project.technology, "Django")
        self.assertTrue(project.is_featured)
        self.assertEqual(project.starred_by.count(), 0)

    def test_invalid_inputs_return_field_errors_without_saving(self):
        self.client.force_login(self.owner)
        for field, value in (
            ("title", "   "), ("title", '<img src=x onerror="alert(1)">'),
            ("description", "<br>"), ("technology", "<br>"),
            ("repository_url", "javascript:alert(1)"),
            ("project_image_url", "data:text/html,test"), ("title", "a" * 256),
        ):
            with self.subTest(field=field, value=value):
                response = self.client.post(self.url, {**self.payload, field: value})
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json()["errors"])
        self.assertEqual(Project.objects.count(), 0)

    def test_legacy_form_uses_same_cleaning(self):
        form = ProjectForm({**self.payload, "title": "<br>"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_csrf_enforced_and_header_accepted(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(self.url, self.payload).status_code, 403)
        client.get(reverse("main:show_projects"))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.url, self.payload, HTTP_X_CSRFTOKEN=token,
                                    HTTP_ORIGIN="https://attacker.invalid").status_code, 403)
        self.assertEqual(client.post(self.url, self.payload, HTTP_X_CSRFTOKEN=token).status_code, 201)

    def test_json_personalized_and_not_cacheable(self):
        project = Project.objects.create(**self.payload)
        project.starred_by.add(self.member)
        url = reverse("main:get_projects_json")
        for user in (None, self.member, self.owner):
            self.client.logout()
            if user:
                self.client.force_login(user)
            response = self.client.get(url)
            fields = response.json()[0]["fields"]
            self.assertEqual(fields["is_starred"], user == self.member)
            self.assertEqual(fields["star_count"], 1)
            self.assertEqual(fields["starred_by_names"], "ajax-member")
            self.assertNotIn("password", fields)
            self.assertNotIn("email", fields)
            self.assertIn("no-store", response["Cache-Control"])

    def test_shell_and_modal_visibility(self):
        Project.objects.create(**self.payload)
        for user in (None, self.member, self.owner):
            self.client.logout()
            if user:
                self.client.force_login(user)
            response = self.client.get(reverse("main:show_projects"), {"title": "  Django  "})
            self.assertContains(response, 'value="Django"')
            self.assertContains(response, 'id="projects-grid"')
            self.assertContains(response, "js/projects.js")
            self.assertContains(response, "js/toast.js")
            self.assertNotIn("project_list", response.context)
            self.assertNotContains(response, self.payload["description"])
            self.assertEqual(b'id="project-form"' in response.content, user == self.owner)
