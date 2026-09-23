import secrets
import uuid

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core import serializers
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Project


class AuthenticationTest(TestCase):
    def setUp(self):
        self.password = secrets.token_urlsafe(24)
        self.user = get_user_model().objects.create_user("visitor", password=self.password)
        self.login_url = reverse("main:login")
        self.register_url = reverse("main:register")
        self.logout_url = reverse("main:logout")

    def login(self, client=None, **extra):
        return (client or self.client).post(self.login_url, {
            "username": self.user.username, "password": self.password,
        }, **extra)

    def test_public_auth_pages_use_base_and_shared_fields(self):
        for url in (self.login_url, self.register_url):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "base.html")
            self.assertTemplateUsed(response, "components/form_fields.html")
            self.assertContains(response, "csrfmiddlewaretoken")
            self.assertFalse(response.context["form"].is_bound)

    def test_register_hashes_password_without_privileges_or_automatic_login(self):
        response = self.client.post(self.register_url, {
            "username": "new-visitor", "password1": self.password, "password2": self.password,
            "is_superuser": "on", "is_staff": "on",
        }, follow=True)
        self.assertRedirects(response, self.login_url)
        self.assertContains(response, "Account created successfully")
        account = get_user_model().objects.get(username="new-visitor")
        self.assertTrue(account.check_password(self.password))
        self.assertNotEqual(account.password, self.password)
        self.assertFalse(account.is_staff)
        self.assertFalse(account.is_superuser)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_register_rejects_duplicate_mismatch_weak_password_and_empty_post(self):
        for data, field in [
            ({"username": "visitor", "password1": self.password, "password2": self.password}, "username"),
            ({"username": "new", "password1": self.password, "password2": "different"}, "password2"),
            ({"username": "new", "password1": "123", "password2": "123"}, "password2"),
            ({}, "username"),
        ]:
            with self.subTest(field=field):
                response = self.client.post(self.register_url, data)
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_login_creates_session_cookie_and_preserves_owner_profile(self):
        response = self.login()
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(self.client.session["_auth_user_id"], str(self.user.pk))
        self.assertIn("sessionid", response.cookies)
        cookie = response.cookies["last_login"]
        self.assertRegex(cookie.value, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["max-age"], "")
        for url in ("/", "/experience/", "/education/", "/projects/"):
            page = self.client.get(url)
            self.assertContains(page, '<span class="nav-user">visitor</span>', html=True)
            self.assertContains(page, "Mohammad Adzka Aulia")
        self.assertContains(self.client.get("/"), cookie.value)

    def test_https_sets_secure_last_login_cookie(self):
        self.assertTrue(self.login(secure=True).cookies["last_login"]["secure"])

    def test_login_ignores_external_next_url(self):
        response = self.client.post(self.login_url + "?next=https://attacker.invalid", {
            "username": "visitor", "password": self.password, "next": "https://attacker.invalid",
        })
        self.assertRedirects(response, "/")

    def test_bad_and_inactive_login_do_not_create_session_or_cookie(self):
        for inactive in (False, True):
            self.user.is_active = not inactive
            self.user.save()
            response = self.client.post(self.login_url, {
                "username": "visitor", "password": self.password if inactive else "wrong",
            })
            self.assertTrue(response.context["form"].non_field_errors())
            self.assertNotIn("_auth_user_id", self.client.session)
            self.assertNotIn("last_login", response.cookies)

    def test_empty_login_post_shows_validation_errors(self):
        response = self.client.post(self.login_url, {})
        self.assertTrue(response.context["form"].is_bound)
        self.assertEqual(set(response.context["form"].errors), {"username", "password"})

    def test_logout_requires_post_and_flushes_session_and_cookie(self):
        self.login()
        session_key = self.client.session.session_key
        self.assertEqual(self.client.get(self.logout_url).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, "/")
        self.assertEqual(response.cookies["last_login"]["max-age"], 0)
        self.assertFalse(Session.objects.filter(session_key=session_key).exists())
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(get_user_model().objects.filter(pk=self.user.pk).exists())

    def test_missing_or_forged_last_login_cookie_never_authenticates(self):
        self.assertContains(self.client.get("/"), "No login cookie available")
        self.client.cookies["last_login"] = "<script>alert(1)</script>"
        response = self.client.get("/")
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_auth_posts_enforce_csrf_including_logout(self):
        client = Client(enforce_csrf_checks=True)
        for url in (self.register_url, self.login_url, self.logout_url):
            self.assertEqual(client.post(url, {}).status_code, 403)
        client.get(self.login_url)
        response = client.post(self.login_url, {
            "username": "visitor", "password": self.password,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
        })
        self.assertRedirects(response, "/")
        self.assertEqual(client.post(self.logout_url).status_code, 403)
        # Django rotates CSRF on login; use the newly issued token.
        response = client.post(self.logout_url, {"csrfmiddlewaretoken": client.cookies["csrftoken"].value})
        self.assertRedirects(response, "/")

    def test_auth_pages_reject_unsupported_methods(self):
        for url in (self.register_url, self.login_url, self.logout_url):
            self.assertEqual(self.client.put(url).status_code, 405)


class ProjectAuthorizationTest(TestCase):
    def setUp(self):
        self.member = get_user_model().objects.create_user("star-member")
        self.other = get_user_model().objects.create_user("other-member")
        self.staff = get_user_model().objects.create_user("staff-member", is_staff=True)
        self.owner = get_user_model().objects.create_user("owner", is_staff=True, is_superuser=True)
        self.project = Project.objects.create(title="Sample", description="A test project.", technology="Django")
        self.star_url = reverse("main:toggle_star", args=[self.project.pk])
        self.delete_url = reverse("main:delete_project", args=[self.project.pk])
        self.add_url = reverse("main:create_project")

    def test_anonymous_write_requests_redirect_to_login_without_mutation(self):
        for url in (self.add_url, self.delete_url, self.star_url):
            response = self.client.post(url)
            self.assertRedirects(response, f'{reverse("main:login")}?next={url}')
        self.assertEqual(self.client.get(self.add_url).status_code, 302)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_members_and_staff_cannot_create_or_delete_projects(self):
        for account in (self.member, self.staff):
            self.client.force_login(account)
            self.assertEqual(self.client.get(self.add_url).status_code, 403)
            self.assertEqual(self.client.post(self.add_url, {"title": "Attempt"}).status_code, 403)
            self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_controls_match_role_but_star_is_visible_to_everyone(self):
        for account in (None, self.member, self.staff, self.owner):
            self.client.logout()
            if account:
                self.client.force_login(account)
            response = self.client.get(reverse("main:show_projects"))
            self.assertContains(response, self.star_url)
            if account == self.owner:
                self.assertContains(response, self.add_url)
                self.assertContains(response, self.delete_url)
            else:
                self.assertNotContains(response, self.add_url)
                self.assertNotContains(response, self.delete_url)

    def test_star_and_unstar_only_affect_the_logged_in_user(self):
        self.project.starred_by.add(self.other)
        self.client.force_login(self.member)
        response = self.client.post(self.star_url, {"user_id": self.other.pk}, follow=True)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertContains(response, 'aria-pressed="true"')
        self.assertContains(response, '<span class="star-count">2</span>', html=True)
        self.assertEqual(set(self.project.starred_by.all()), {self.member, self.other})
        self.client.post(self.star_url)
        self.assertEqual(list(self.project.starred_by.all()), [self.other])
        self.assertEqual(Project.objects.count(), 1)

    def test_superuser_can_star_too(self):
        self.client.force_login(self.owner)
        self.assertRedirects(self.client.post(self.star_url), reverse("main:show_projects"))
        self.assertTrue(self.project.starred_by.filter(pk=self.owner.pk).exists())

    def test_get_star_and_get_delete_never_mutate(self):
        self.client.force_login(self.owner)
        for url in (self.star_url, self.delete_url):
            self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.project.starred_by.count(), 0)
        self.assertEqual(Project.objects.count(), 1)

    def test_star_missing_project_returns_404(self):
        self.client.force_login(self.member)
        self.assertEqual(self.client.post(reverse("main:toggle_star", args=[uuid.uuid4()])).status_code, 404)

    def test_star_requires_csrf_and_accepts_header_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.member)
        self.assertEqual(client.post(self.star_url).status_code, 403)
        client.get(reverse("main:show_projects"))
        token = client.cookies["csrftoken"].value
        self.assertRedirects(client.post(self.star_url, HTTP_X_CSRFTOKEN=token), reverse("main:show_projects"))

    def test_natural_keys_expose_username_not_user_id_or_private_fields(self):
        self.project.starred_by.add(self.member)
        response = self.client.get(reverse("main:get_projects_json"))
        fields = response.json()[0]["fields"]
        self.assertEqual(fields["starred_by"], [["star-member"]])
        self.assertNotIn("password", fields)
        self.assertNotIn("email", fields)
        for name, format_ in (("get_projects_json", "json"), ("get_projects_xml", "xml")):
            response = self.client.get(reverse(f"main:{name}"))
            deserialized = list(serializers.deserialize(format_, response.content.decode()))
            self.assertEqual(deserialized[0].m2m_data["starred_by"], [self.member.pk])
        page = self.client.get(reverse("main:show_projects"))
        self.assertContains(page, "Starred by star-member")

    def test_project_form_cannot_forge_star_membership(self):
        self.client.force_login(self.owner)
        self.client.post(self.add_url, {
            "title": "New", "description": "Test", "technology": "Django",
            "starred_by": [self.member.pk],
        })
        self.assertEqual(Project.objects.get(title="New").starred_by.count(), 0)

    def test_public_portfolio_and_apis_stay_accessible(self):
        for url in ("/", "/experience/", "/education/", "/projects/", self.project.get_absolute_url(),
                    "/api/projects/", "/api/projects/xml/", "/api/education/", "/api/experience/"):
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_new_user_does_not_gain_education_admin_access(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("main:create_education"), {})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("admin:login")))
