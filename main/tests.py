from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project


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
