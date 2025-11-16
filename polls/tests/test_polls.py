from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from polls.models import Poll

class TestPolls(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin"
        )

        self.voter = User.objects.create_user(
            username="voter",
            email="voter@example.com",
            password="voter123",
            role="voter"
        )

    def authenticate(self, user):
        res = self.client.post("/api/auth/login/", {
            "email": user.email,
            "password": user.password_raw if hasattr(user, "password_raw") else "admin123"
        })
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.data["access"])

    def test_list_polls_public(self):
        res = self.client.get("/api/polls/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_admin_can_create_poll(self):
        self.authenticate(self.admin)

        res = self.client.post("/api/polls/", {
            "title": "New Poll",
            "description": "Test description",
            "expires_at": None,
            "is_active": True,
        },
        format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Poll.objects.count(), 1)

    # def test_voter_cannot_create_poll(self):
    #     self.authenticate(self.voter)

    #     res = self.client.post("/api/polls/", {
    #         "title": "Invalid Poll",
    #         "description": "Test",
    #     })

    #     self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
