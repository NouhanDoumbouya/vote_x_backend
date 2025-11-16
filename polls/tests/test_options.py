from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from polls.models import Poll, Option

class TestOptions(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin"
        )
        self.poll = Poll.objects.create(
            title="Languages",
            description="Choose one",
            created_by=self.admin
        )

    def authenticate(self):
        res = self.client.post("/api/auth/login/", {
            "email": "admin@example.com",
            "password": "admin123"
        })
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.data["access"])

    def test_add_option(self):
        self.authenticate()

        res = self.client.post(f"/api/polls/{self.poll.id}/options/", {
            "text": "Python"
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Option.objects.count(), 1)

    def test_list_options(self):
        Option.objects.create(poll=self.poll, text="Python")
        Option.objects.create(poll=self.poll, text="Rust")

        res = self.client.get(f"/api/polls/{self.poll.id}/options/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 4)
