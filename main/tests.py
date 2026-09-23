import uuid
from xml.etree import ElementTree

from django.core import serializers
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project
from main.forms import ProjectForm


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Web Developer",
            description="Developing responsive web interfaces and applications.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(
            response,
            f'href="{reverse("main:show_experience")}"',
        )

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)


    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Web Developer")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Ongoing")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()

        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "No experience added yet.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Completed")
        self.assertNotContains(response, "Ongoing")


class ProjectDeliveryTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Portfolio & Notes",
            description="A <small> Django project.",
            technology="Django, HTML",
            is_featured=True,
        )
        self.other = Project.objects.create(
            title="Study Planner", description="Plan a semester.", technology="Python"
        )
        self.payload = {
            "title": "New Project",
            "description": "A project submitted through the form.",
            "technology": "Django",
        }
        self.add_url = reverse("main:create_project")
        self.list_url = reverse("main:show_projects")
        self.delete_url = reverse("main:delete_project", args=[self.project.pk])
        self.owner = get_user_model().objects.create_user(
            username="project-test-owner", is_staff=True, is_superuser=True
        )
        self.client.force_login(self.owner)

    def test_form_exposes_only_editable_fields(self):
        self.assertEqual(list(ProjectForm().fields), [
            "title", "description", "technology", "repository_url",
            "project_image_url", "is_featured",
        ])

    def test_get_add_form_does_not_create_project(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertFalse(response.context["form"].is_bound)
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertEqual(Project.objects.count(), 2)

    def test_valid_post_creates_project_and_shows_message_once(self):
        response = self.client.post(self.add_url, self.payload, follow=True)
        self.assertRedirects(response, self.list_url)
        self.assertContains(response, "Project added successfully!")
        project = Project.objects.get(title="New Project")
        self.assertEqual(project.repository_url, "")
        self.assertEqual(project.project_image_url, "")
        self.assertFalse(project.is_featured)
        self.assertNotContains(self.client.get(self.list_url), "Project added successfully!")

    def test_optional_fields_are_saved_and_image_rendered(self):
        response = self.client.post(self.add_url, {
            **self.payload,
            "repository_url": "https://example.com/source",
            "project_image_url": "https://example.com/preview.png",
            "is_featured": "on",
        }, follow=True)
        project = Project.objects.get(title="New Project")
        self.assertTrue(project.is_featured)
        self.assertEqual(project.repository_url, "https://example.com/source")
        self.assertContains(response, 'src="https://example.com/preview.png"')
        self.assertContains(self.client.get(project.get_absolute_url()), project.project_image_url)

    def test_invalid_form_keeps_input_and_does_not_save(self):
        response = self.client.post(self.add_url, {
            **self.payload, "repository_url": "not-a-url",
            "project_image_url": "javascript:alert(1)",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("repository_url", response.context["form"].errors)
        self.assertIn("project_image_url", response.context["form"].errors)
        self.assertContains(response, 'value="New Project"')
        self.assertEqual(Project.objects.count(), 2)

    def test_empty_post_shows_required_field_errors(self):
        response = self.client.post(self.add_url, {})
        self.assertTrue(response.context["form"].is_bound)
        self.assertEqual(set(response.context["form"].errors), {"title", "description", "technology"})
        self.assertEqual(Project.objects.count(), 2)

    def test_json_response_preserves_fields_and_uuid(self):
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["pk"], str(self.project.pk))
        self.assertEqual(data[0]["model"], "main.project")
        self.assertEqual(data[0]["fields"]["title"], self.project.title)

    def test_xml_is_parseable_and_round_trips_special_characters(self):
        response = self.client.get(reverse("main:get_projects_xml"))
        self.assertEqual(response["Content-Type"], "application/xml")
        root = ElementTree.fromstring(response.content)
        self.assertEqual(root.tag, "django-objects")
        projects = list(serializers.deserialize("xml", response.content.decode("utf-8")))
        self.assertEqual(projects[0].object.description, self.project.description)
        self.assertEqual(projects[0].object.pk, self.project.pk)

    def test_title_search_is_trimmed_and_case_insensitive_on_all_read_routes(self):
        for name in ("show_projects", "get_projects_json", "get_projects_xml"):
            with self.subTest(route=name):
                response = self.client.get(reverse(f"main:{name}"), {"title": "  pOrTfOlIo  "})
                self.assertContains(response, "Portfolio")
                self.assertNotContains(response, self.other.title)
        self.assertEqual(response.status_code, 200)

    def test_blank_search_returns_all_projects(self):
        response = self.client.get(self.list_url, {"title": "   "})
        self.assertEqual(len(response.context["project_list"]), 2)
        self.assertEqual(response.context["title_query"], "")

    def test_search_with_no_match_returns_empty_response(self):
        response = self.client.get(self.list_url, {"title": "missing-project"})
        self.assertContains(response, "No projects match")
        self.assertEqual(response.context["project_list"], [])
        self.assertEqual(self.client.get(reverse("main:get_projects_json"), {"title": "missing-project"}).json(), [])

    def test_empty_database_serializes_in_both_formats(self):
        Project.objects.all().delete()
        self.assertEqual(self.client.get(reverse("main:get_projects_json")).json(), [])
        response = self.client.get(reverse("main:get_projects_xml"))
        self.assertEqual(list(serializers.deserialize("xml", response.content.decode("utf-8"))), [])

    def test_html_escapes_stored_content_and_search_query(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, "A &lt;small&gt; Django project.")
        response = self.client.get(self.list_url, {"title": '<script>alert("x")</script>'})
        self.assertNotContains(response, "<script>")

    def test_get_delete_does_not_delete(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_delete_post_removes_only_target_and_redirects(self):
        response = self.client.post(self.delete_url, follow=True)
        self.assertRedirects(response, self.list_url)
        self.assertContains(response, "Project deleted successfully!")
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        self.assertTrue(Project.objects.filter(pk=self.other.pk).exists())

    def test_missing_project_delete_returns_404(self):
        response = self.client.post(reverse("main:delete_project", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Project.objects.count(), 2)

    def test_write_routes_reject_missing_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(self.add_url, self.payload).status_code, 403)
        self.assertEqual(client.post(self.delete_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 2)

    def test_csrf_accepts_trusted_pws_origin_and_rejects_other_origins(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        client.get(self.add_url)
        token = client.cookies["csrftoken"].value
        response = client.post(self.add_url, {
            **self.payload, "csrfmiddlewaretoken": token,
        }, HTTP_ORIGIN="https://attacker.invalid")
        self.assertEqual(response.status_code, 403)
        response = client.post(self.add_url, {
            **self.payload, "csrfmiddlewaretoken": token,
        }, HTTP_ORIGIN="https://mohammad-adzka-myportofolio.pws.cs.ui.ac.id")
        self.assertRedirects(response, self.list_url)
        response = client.post(self.delete_url, {"csrfmiddlewaretoken": token})
        self.assertRedirects(response, self.list_url)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_confirmation_component_has_unique_targets_and_csrf(self):
        response = self.client.get(self.list_url)
        self.assertTemplateUsed(response, "components/project_delete_modal.html")
        for project in (self.project, self.other):
            self.assertContains(response, f'id="delete-project-{project.pk}"', count=1)
            self.assertContains(response, reverse("main:delete_project", args=[project.pk]))
        # One logout form, two star forms, and two delete forms.
        self.assertContains(response, 'name="csrfmiddlewaretoken"', count=5)

    def test_read_endpoints_reject_post_and_create_rejects_delete(self):
        for name in ("show_projects", "get_projects_json", "get_projects_xml"):
            with self.subTest(route=name):
                self.assertEqual(self.client.post(reverse(f"main:{name}")).status_code, 405)
        self.assertEqual(self.client.delete(self.add_url).status_code, 405)

class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="My Portfolio",
            description="A personal portfolio website built with Django.",
            technology="Django, HTML5, CSS3",
            repository_url="https://github.com/hollow011/myportofolio",
            is_featured=True,
        )

    def test_project_list_url_uses_correct_template(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_project_data_appears_on_list_page(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, self.project.technology)
        self.assertContains(response, self.project.get_absolute_url())

    def test_empty_project_page_displays_message(self):
        Project.objects.all().delete()

        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, "No projects added yet.")

    def test_project_detail_page(self):
        response = self.client.get(self.project.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project_detail.html")
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.repository_url)

    def test_missing_project_detail_returns_404(self):
        missing_project_url = reverse(
            "main:show_project_detail",
            kwargs={"project_id": "00000000-0000-0000-0000-000000000000"},
        )

        response = self.client.get(missing_project_url)

        self.assertEqual(response.status_code, 404)
