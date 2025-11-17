from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User


class TestAuth(APITestCase):

    def test_user_registration(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "role": "voter",
        }

        res = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_user_login(self):
        User.objects.create_user(
            username="test",
            email="test@example.com",
            password="password123",
            role="voter",
        )

        data = {"email": "test@example.com", "password": "password123"}
        res = self.client.post("/api/auth/login/", data, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_invalid_login(self):
        res = self.client.post(
            "/api/auth/login/",
            {"email": "wrong@example.com", "password": "abc123"},
            format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
