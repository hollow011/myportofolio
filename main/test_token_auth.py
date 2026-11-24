from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class TokenAuthTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser("token-owner", password="test-password")
        self.visitor = User.objects.create_user("token-visitor", password="test-password")
        self.payload = {"title": "Mobile", "description": "From Flutter", "tech_stack": "Dart",
                        "project_url": "https://example.com", "project_image_url": ""}

    def login_token(self, username):
        response = self.client.post(reverse("api:token-auth"),
                                    {"username": username, "password": "test-password"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + response.data["token"])
        return response.data["token"]

    def test_public_read_token_create_and_revocation(self):
        self.assertEqual(self.client.get(reverse("api:project-list")).status_code, 200)
        key = self.login_token("token-owner")
        created = self.client.post(reverse("api:project-list"), self.payload, format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["tech_stack"], "Dart")
        other = Token.objects.create(user=self.visitor)
        response = self.client.post(reverse("api:logout"))
        self.assertEqual((response.status_code, response.content), (204, b""))
        self.assertFalse(Token.objects.filter(key=key).exists())
        self.assertTrue(Token.objects.filter(key=other.key).exists())
        self.assertEqual(self.client.post(reverse("api:project-list"), self.payload, format="json").status_code, 401)

    def test_non_owner_token_cannot_create(self):
        self.login_token("token-visitor")
        self.assertEqual(self.client.post(reverse("api:project-list"), self.payload, format="json").status_code, 403)

    def test_invalid_login_and_unauthenticated_logout(self):
        self.assertEqual(self.client.post(reverse("api:token-auth"),
                         {"username": "token-owner", "password": "wrong"}, format="json").status_code, 400)
        self.assertEqual(self.client.post(reverse("api:logout")).status_code, 401)

    def test_session_still_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(reverse("api:project-list"), self.payload, format="json").status_code, 403)

    def test_cors_only_allows_local_api_origins(self):
        response = self.client.options(reverse("api:project-list"), HTTP_ORIGIN="http://localhost:8768",
                                       HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
                                       HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type")
        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:8768")
        denied = self.client.options(reverse("api:project-list"), HTTP_ORIGIN="https://untrusted.example",
                                     HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST")
        self.assertNotIn("Access-Control-Allow-Origin", denied)
