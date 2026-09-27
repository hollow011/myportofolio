from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from main.models import Project


class PortfolioDesignTest(TestCase):
    def test_home_retains_identity_skills_cookie_and_semantic_landmarks(self):
        self.client.cookies["last_login"] = "2026-09-27 20:00:00"
        response = self.client.get(reverse("main:show_main"))
        for text in ("Mohammad Adzka Aulia", "2506657005", "S1 Ilmu Komputer",
                     "2026-09-27 20:00:00", "Web Development", "Python &amp; Django",
                     "Workspace Mentality", 'id="skills"', 'id="about"',
                     '<main id="main-content"', 'href="#main-content"'):
            self.assertContains(response, text)
        self.assertContains(response, "<!doctype html>", count=1)

    def test_home_uses_at_most_three_real_projects_with_featured_first(self):
        for index in range(4):
            Project.objects.create(title=f"Real project {index}", description="Test",
                                   technology="Django", is_featured=index == 0)
        response = self.client.get(reverse("main:show_main"))
        projects = list(response.context["featured_projects"])
        self.assertEqual(len(projects), 3)
        self.assertTrue(projects[0].is_featured)
        for project in projects:
            self.assertContains(response, project.title)
            self.assertContains(response, project.get_absolute_url())

    def test_home_empty_state_links_to_projects_without_invented_records(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, "EVERY PROJECT STARTS")
        self.assertContains(response, reverse("main:show_projects"))
        self.assertEqual(Project.objects.count(), 0)

    def test_home_project_content_is_escaped(self):
        Project.objects.create(title="<script>alert(1)</script>", description="Test",
                               technology="<b>Django</b>")
        response = self.client.get(reverse("main:show_main"))
        self.assertNotContains(response, "<script>")
        self.assertContains(response, "&lt;script&gt;")
        self.assertContains(response, "&lt;b&gt;Django&lt;/b&gt;")

    def test_shared_navigation_preserves_routes_on_each_public_page(self):
        for url in ("/", "/projects/", "/experience/", "/education/", "/login/", "/register/"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, '<details class="menu" id="site-menu">')
                self.assertContains(response, 'aria-label="Primary navigation"')
                self.assertContains(response, 'href="#main-content"')
                for name in ("show_main", "show_projects", "show_experience", "show_education"):
                    self.assertContains(response, f'href="{reverse("main:" + name)}"')
                self.assertContains(response, "Sign in ↗")

    def test_signed_in_identity_remains_visible_and_logout_is_post_with_csrf(self):
        user = get_user_model().objects.create_user("design-reader")
        self.client.force_login(user)
        response = self.client.get(reverse("main:show_main"))
        self.assertContains(response, 'title="Signed in as design-reader"')
        self.assertContains(response, 'action="/logout/"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"', count=1)
        self.assertNotContains(response, 'href="/logout/"')
        self.assertNotContains(response, "Sign in ↗")
