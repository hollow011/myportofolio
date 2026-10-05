import secrets
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import IntegrityError, transaction
from django.template.loader import get_template
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from main.forms import EducationForm
from main.models import Education


class TemplateCompilationTest(SimpleTestCase):
    def test_every_template_compiles_after_formatting(self):
        root = Path(settings.BASE_DIR) / "templates"
        for path in root.rglob("*.html"):
            with self.subTest(template=path.name):
                get_template(str(path.relative_to(root)))


class EducationAuthorizationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.member = users.create_user("education-member", email="private@example.invalid")
        cls.editor = users.create_user("education-editor")
        cls.editor_group = Group.objects.create(name="Editor")
        cls.editor.groups.add(cls.editor_group)
        cls.staff = users.create_user("staff-only", is_staff=True)
        # Superuser does not need is_staff for the public Education views.
        cls.owner = users.create_user("education-owner", is_superuser=True)
        cls.payload = {"institution": "Test University", "degree": "bachelor",
                       "field_of_study": "Computer Science"}
        cls.education = Education.objects.create(**cls.payload)
        cls.list_url = reverse("main:show_education")
        cls.detail_url = cls.education.get_absolute_url()
        cls.add_url = reverse("main:create_education")
        cls.edit_url = reverse("main:update_education", args=[cls.education.pk])
        cls.delete_url = reverse("main:delete_education", args=[cls.education.pk])
        cls.star_url = reverse("main:toggle_education_star", args=[cls.education.pk])
        cls.json_url = reverse("main:get_education_json")

    def test_public_read_access_for_all_roles(self):
        for account in (None, self.member, self.editor, self.staff, self.owner):
            self.client.logout()
            if account:
                self.client.force_login(account)
            for url in (self.list_url, self.detail_url, self.json_url):
                with self.subTest(account=account, url=url):
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_anonymous_write_requests_redirect_to_normal_login(self):
        for url in (self.add_url, self.edit_url, self.delete_url, self.star_url):
            response = self.client.post(url, self.payload)
            self.assertRedirects(response, f'{reverse("main:login")}?next={url}')
        for url in (self.add_url, self.edit_url):
            self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(Education.objects.count(), 1)
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_member_and_staff_get_403_without_data_changes(self):
        for account in (self.member, self.staff):
            self.client.force_login(account)
            for url in (self.add_url, self.edit_url, self.delete_url):
                self.assertEqual(self.client.post(url, self.payload).status_code, 403)
            for url in (self.add_url, self.edit_url):
                self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, self.payload["institution"])

    def test_editor_can_only_edit_existing_content(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(self.edit_url).status_code, 200)
        response = self.client.post(self.edit_url, {**self.payload, "institution": "Edited"})
        self.assertRedirects(response, self.list_url)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Edited")
        self.assertEqual(self.client.get(self.add_url).status_code, 403)
        for url in (self.add_url, self.delete_url):
            self.assertEqual(self.client.post(url, self.payload).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)

    def test_superuser_without_staff_can_create_edit_delete(self):
        self.client.force_login(self.owner)
        self.assertRedirects(self.client.post(self.add_url, self.payload), self.list_url)
        self.assertRedirects(self.client.post(self.edit_url, self.payload), self.list_url)
        self.assertRedirects(self.client.post(self.delete_url), self.list_url)
        self.assertFalse(Education.objects.filter(pk=self.education.pk).exists())
        self.assertEqual(Education.objects.count(), 1)

    def test_controls_follow_roles_on_list_and_detail(self):
        for account in (None, self.member, self.staff, self.editor, self.owner):
            self.client.logout()
            if account:
                self.client.force_login(account)
            for url in (self.list_url, self.detail_url):
                response = self.client.get(url)
                if url == self.list_url:
                    self.assertContains(response, 'data-star-url=')
                    self.assertContains(response, 'data-can-edit="' + ("true" if account in (self.editor, self.owner) else "false") + '"')
                    self.assertContains(response, 'data-can-delete="' + ("true" if account == self.owner else "false") + '"')
                    self.assertEqual(b'id="education-form"' in response.content, account == self.owner)
                    continue
                self.assertContains(response, self.star_url)
                for action, allowed in (
                    (self.edit_url, account in (self.editor, self.owner)),
                    (self.delete_url, account == self.owner),
                ):
                    if allowed:
                        self.assertContains(response, action)
                    else:
                        self.assertNotContains(response, action)

    def test_revoking_editor_group_takes_effect_next_request(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(self.edit_url).status_code, 200)
        self.editor.groups.remove(self.editor_group)
        self.assertEqual(self.client.post(self.edit_url, self.payload).status_code, 403)
        self.assertNotContains(self.client.get(self.list_url), self.edit_url)

    def test_inactive_editor_and_owner_cannot_mutate(self):
        for account in (self.editor, self.owner):
            account.is_active = False
            account.save()
            self.client.force_login(account)
            for url in (self.add_url, self.edit_url, self.delete_url, self.star_url):
                self.assertEqual(self.client.post(url, self.payload).status_code, 302)
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_forged_role_or_star_fields_cannot_escalate(self):
        self.client.force_login(self.member)
        forged = {**self.payload, "groups": [self.editor_group.pk],
                  "is_superuser": "on", "is_staff": "on", "is_editor": "true"}
        self.assertEqual(self.client.post(self.edit_url, forged).status_code, 403)
        self.client.force_login(self.editor)
        forged["starred_by"] = [self.owner.pk]
        self.assertRedirects(self.client.post(self.edit_url, forged), self.list_url)
        self.assertEqual(self.education.starred_by.count(), 0)
        self.assertNotIn("starred_by", EducationForm().fields)

    def test_registration_cannot_assign_editor_group(self):
        password = secrets.token_urlsafe(24)
        self.client.post(reverse("main:register"), {
            "username": "attempted-editor", "password1": password, "password2": password,
            "groups": [self.editor_group.pk], "is_staff": "on", "is_superuser": "on",
        })
        account = get_user_model().objects.get(username="attempted-editor")
        self.assertEqual(account.groups.count(), 0)
        self.assertFalse(account.is_staff or account.is_superuser)

    def test_authorized_unknown_uuids_return_404(self):
        self.client.force_login(self.owner)
        for name in ("update_education", "delete_education", "toggle_education_star"):
            url = reverse(f"main:{name}", args=[uuid.uuid4()])
            self.assertEqual(self.client.post(url, self.payload).status_code, 404)
        self.assertEqual(self.client.get(reverse(
            "main:show_education_detail", args=[uuid.uuid4()]
        )).status_code, 404)

    def test_mutating_get_and_unsupported_methods_are_rejected(self):
        self.client.force_login(self.owner)
        for url in (self.star_url, self.delete_url):
            self.assertEqual(self.client.get(url).status_code, 405)
        for url in (self.add_url, self.edit_url, self.star_url, self.delete_url):
            self.assertEqual(self.client.put(url).status_code, 405)
        self.assertEqual(self.client.post(self.detail_url).status_code, 405)

    def test_each_authenticated_role_can_star_and_unstar(self):
        for account in (self.member, self.editor, self.staff, self.owner):
            self.client.force_login(account)
            response = self.client.post(self.star_url, follow=True)
            self.assertRedirects(response, self.list_url)
            fields = self.client.get(self.json_url).json()[0]["fields"]
            self.assertTrue(fields["is_starred"])
            self.assertEqual(fields["star_count"], 1)
            self.assertContains(self.client.get(self.detail_url), 'aria-pressed="true"')
            self.client.post(self.star_url)
            self.assertEqual(self.education.starred_by.count(), 0)
            self.assertContains(self.client.get(self.detail_url), 'aria-pressed="false"')

    def test_star_uses_session_identity_not_post_data(self):
        self.education.starred_by.add(self.owner)
        self.client.force_login(self.member)
        self.client.post(self.star_url, {"user_id": self.owner.pk, "starred_by": self.editor.pk})
        self.assertEqual(set(self.education.starred_by.all()), {self.owner, self.member})
        self.client.post(self.star_url, {"user_id": self.owner.pk})
        self.assertEqual(list(self.education.starred_by.all()), [self.owner])

    def test_database_enforces_one_star_per_user(self):
        self.education.starred_by.add(self.member, self.member)
        self.assertEqual(self.education.starred_by.count(), 1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Education.starred_by.through.objects.create(
                education_id=self.education.pk, user_id=self.member.pk
            )

    def test_csrf_required_for_star_and_editor_update(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.editor)
        for url in (self.edit_url, self.star_url):
            self.assertEqual(client.post(url, self.payload).status_code, 403)
        client.get(self.list_url)
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(self.star_url, HTTP_X_CSRFTOKEN=token,
                                    HTTP_ORIGIN="https://attacker.invalid").status_code, 403)
        self.assertRedirects(client.post(self.star_url, HTTP_X_CSRFTOKEN=token), self.list_url)
        self.assertRedirects(client.post(self.edit_url, {
            **self.payload, "csrfmiddlewaretoken": token,
        }), self.list_url)

    def test_json_retains_filter_and_exposes_only_public_star_metadata(self):
        self.education.starred_by.add(self.member)
        response = self.client.get(self.json_url, {"institution": "  TEST  "})
        fields = response.json()[0]["fields"]
        self.assertEqual(set(fields), {"institution", "degree", "field_of_study",
                                     "description", "website", "is_current",
                                     "created_at", "degree_display", "star_count",
                                     "is_starred", "starred_by_names"})
        self.assertEqual(fields["starred_by_names"], self.member.username)
        self.assertEqual(fields["star_count"], 1)
        self.assertFalse(fields["is_starred"])
        for private in (self.member.email, self.member.password, "is_superuser", "session_key"):
            self.assertNotContains(response, private)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(self.client.get(self.json_url, {"institution": "absent"}).json(), [])

    def test_star_is_not_lost_on_edit_and_is_removed_with_education(self):
        self.education.starred_by.add(self.member)
        self.client.force_login(self.owner)
        self.client.post(self.edit_url, self.payload)
        self.assertEqual(self.education.starred_by.count(), 1)
        self.client.post(self.delete_url)
        self.assertEqual(Education.starred_by.through.objects.count(), 0)
        self.assertTrue(get_user_model().objects.filter(pk=self.member.pk).exists())

    def test_detail_escapes_untrusted_content(self):
        self.education.institution = '<script>alert("x")</script>'
        self.education.description = '<script>alert("y")</script>'
        self.education.save()
        response = self.client.get(self.detail_url)
        self.assertNotContains(response, "<script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_admin_cannot_bypass_role_checks_with_model_permissions(self):
        # Even a staff account with all Education model permissions is not an owner.
        self.staff.user_permissions.set(Permission.objects.filter(
            content_type__app_label="main", content_type__model="education"
        ))
        self.client.force_login(self.staff)
        admin_add = reverse("admin:main_education_add")
        admin_edit = reverse("admin:main_education_change", args=[self.education.pk])
        admin_delete = reverse("admin:main_education_delete", args=[self.education.pk])
        for url in (admin_add, admin_edit, admin_delete):
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, self.payload).status_code, 403)
        self.staff.groups.add(self.editor_group)
        self.assertEqual(self.client.get(admin_edit).status_code, 200)
        self.assertRedirects(self.client.post(admin_edit, {**self.payload, "_save": "Save"}),
                             reverse("admin:main_education_changelist"))
        for url in (admin_add, admin_delete):
            self.assertEqual(self.client.post(url, self.payload).status_code, 403)
        # Bulk delete must also be unavailable to an editor.
        changelist = reverse("admin:main_education_changelist")
        self.client.post(changelist, {"action": "delete_selected",
                                     "_selected_action": [self.education.pk], "post": "yes"})
        self.assertTrue(Education.objects.filter(pk=self.education.pk).exists())

    def test_nonstaff_editor_cannot_enter_admin(self):
        self.client.force_login(self.editor)
        self.assertEqual(self.client.get(reverse("admin:main_education_changelist")).status_code, 302)
        self.assertEqual(self.client.get(self.edit_url).status_code, 200)
