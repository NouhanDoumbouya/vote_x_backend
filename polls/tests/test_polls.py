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

    def authenticate(self, user: User):
        """Login using JWT and attach Authorization header."""
        res = self.client.post(
            "/api/auth/login/",
            {
                "email": user.email,
                "password": "admin123" if user.role == "admin" else "voter123"
            }
        )
        self.assertEqual(res.status_code, 200, res.data)
        token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_polls_public(self):
        """Anyone (guest) can list public polls."""
        res = self.client.get("/api/polls/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_create_poll(self):
        """Any authenticated user (not admin-only) can create polls."""
        self.authenticate(self.voter)

        payload = {
            "title": "New Poll",
            "description": "Test description",
            "category": "General",
            "expires_at": None,
            "visibility": "public",
            "allow_guest_votes": True,
            "options": ["Option A", "Option B"]
        }

        res = self.client.post("/api/polls/", payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        self.assertEqual(Poll.objects.count(), 1)
        poll = Poll.objects.first()
        self.assertEqual(poll.owner, self.voter)
