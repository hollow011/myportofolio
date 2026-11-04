import uuid

from django.contrib.auth.models import Group, User
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Project


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class ProjectAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_superuser("owner", "owner@example.test", "test-password")
        cls.visitor = User.objects.create_user("visitor", password="test-password")
        cls.project = Project.objects.create(title="Portfolio", description="My website", technology="Django")
        cls.list_url = reverse("api:project-list")
        cls.detail_url = reverse("api:project-detail", args=[cls.project.pk])
        cls.star_url = reverse("api:project-star", args=[cls.project.pk])
        cls.payload = {"title": "New project", "description": "A useful app", "tech_stack": "Python",
                       "project_url": "https://example.com/", "project_image_url": "", "is_featured": True}

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["id"], str(self.project.pk))
        self.assertEqual(response.data[0]["tech_stack"], "Django")
        self.assertFalse(response.data[0]["is_starred"])
        self.assertEqual(self.client.get(self.detail_url).data, response.data[0])
        self.assertFalse({"fields", "starred_by", "email", "password"} & response.data[0].keys())

    def test_search_and_empty_results(self):
        self.assertEqual(len(self.client.get(self.list_url, {"title": " PORT "}).data), 1)
        empty = self.client.get(self.list_url, {"title": "missing"})
        self.assertEqual((empty.status_code, empty.data), (200, []))

    def test_missing_project(self):
        missing = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing).status_code, 404)
        self.assertEqual(self.client.patch(missing, {}, format="json").status_code, 403)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")
        self.assertEqual(Project.objects.count(), 1)

    def test_owner_can_create(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.list_url, {**self.payload, "title": " <b>New</b> "}, format="json")
        self.assertEqual(response.status_code, 201)
        saved = Project.objects.get(pk=response.data["id"])
        self.assertEqual((saved.title, saved.technology, saved.repository_url, saved.is_featured),
                         ("New", "Python", "https://example.com/", True))

    def test_validation(self):
        self.client.force_authenticate(self.owner)
        for field, value in (("title", "  "), ("title", "<img onerror=alert(1)>"), ("description", "<b></b>"),
                             ("tech_stack", "<b></b>"), ("project_url", "javascript:alert(1)")):
            with self.subTest(field=field, value=value):
                response = self.client.post(self.list_url, {**self.payload, field: value}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(self.owner)
        changed = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(changed.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual((self.project.title, self.project.description), ("Changed", "My website"))
        self.assertEqual(self.client.put(self.detail_url, {"title": "Incomplete"}, format="json").status_code, 400)
        replaced = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual((replaced.status_code, replaced.data["title"]), (200, "New project"))
        deleted = self.client.delete(self.detail_url)
        self.assertEqual((deleted.status_code, deleted.content), (204, b""))
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.assertEqual(self.client.get(self.star_url).status_code, 403)
        self.client.force_authenticate(self.visitor)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)
        for expected in (True, False):
            response = self.client.post(self.star_url, {"user": self.owner.pk}, format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["is_starred"], expected)
            self.assertEqual(response.data["star_count"], int(expected))
            self.assertEqual(response.data["starred_by_names"], "visitor" if expected else "")
            self.assertEqual(self.project.starred_by.filter(pk=self.visitor.pk).exists(), expected)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(self.owner)
        forged = {"id": str(uuid.uuid4()), "star_count": 99, "is_starred": True,
                  "starred_by_names": "forged", "starred_by": [self.visitor.pk]}
        response = self.client.post(self.list_url, {**self.payload, **forged}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], forged["id"])
        self.assertEqual((response.data["star_count"], response.data["is_starred"], response.data["starred_by_names"]),
                         (0, False, ""))

    def test_staff_and_editor_cannot_manage_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(self.visitor)
        self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)

    def test_wrong_method(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        self.assertEqual(client.get(self.list_url, HTTP_ACCEPT="text/html").status_code, 200)
        response = client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 201)


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class EducationAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.entry = Education.objects.create(institution="School", degree="bachelor", field_of_study="CS")
        cls.list_url = reverse("api:education-list")
        cls.detail_url = reverse("api:education-detail", args=[cls.entry.pk])
        cls.star_url = reverse("api:education-star", args=[cls.entry.pk])
        cls.payload = {"institution": "College", "degree": "master", "field_of_study": "Math"}
        cls.visitor = User.objects.create_user("member")
        cls.editor = User.objects.create_user("editor", password="test-password")
        cls.editor.groups.add(Group.objects.create(name="Editor"))
        cls.owner = User.objects.create_superuser("owner", "owner@example.test")

    def test_public_read_and_member_star(self):
        response = self.client.get(self.list_url, {"institution": " SCH "})
        self.assertEqual([item["degree_display"] for item in response.data], ["Bachelor's degree"])
        self.assertEqual(self.client.get(self.list_url, {"institution": "missing"}).data, [])
        self.assertEqual(self.client.get(self.detail_url).data, response.data[0])
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.client.force_authenticate(self.visitor)
        self.assertTrue(self.client.post(self.star_url).data["is_starred"])
        self.assertFalse(self.client.post(self.star_url).data["is_starred"])
        self.assertEqual(self.client.patch(self.detail_url, self.payload, format="json").status_code, 403)

    def test_editor_can_only_update(self):
        self.client.force_authenticate(self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        response = self.client.patch(self.detail_url, {"institution": "<b>Updated</b>"}, format="json")
        self.assertEqual((response.status_code, response.data["institution"]), (200, "Updated"))
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.field_of_study, "Math")

    def test_editor_session_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="editor", password="test-password"))
        payload = {"institution": "Edited by session"}
        self.assertEqual(client.patch(self.detail_url, payload, format="json").status_code, 403)
        page = client.get(reverse("main:show_education"))
        self.assertEqual(page.status_code, 200)
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.patch(self.detail_url, payload, format="json", HTTP_X_CSRFTOKEN=token).status_code, 200)

    def test_owner_manage_and_validate(self):
        self.client.force_authenticate(self.owner)
        for field, value in (("institution", "<i></i>"), ("field_of_study", " "), ("degree", "invalid"),
                             ("website", "javascript:alert(1)")):
            response = self.client.post(self.list_url, {**self.payload, field: value}, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.data)
        response = self.client.post(self.list_url, {**self.payload, "description": "<i></i>"}, format="json")
        self.assertEqual((response.status_code, response.data["description"]), (201, ""))
        deleted = self.client.delete(reverse("api:education-detail", args=[response.data["id"]]))
        self.assertEqual((deleted.status_code, deleted.content), (204, b""))
