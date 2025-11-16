from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from polls.models import Poll, Option
from votes.models import Vote

class TestVotes(APITestCase):

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

        self.poll = Poll.objects.create(
            title="Favorite Language",
            created_by=self.admin,
            allow_guest_votes=True
        )

        self.option = Option.objects.create(poll=self.poll, text="Python")

    def authenticate(self, user):
        res = self.client.post("/api/auth/login/", {
            "email": user.email,
            "password": "admin123" if user.role == "admin" else "voter123"
        })
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.data["access"])

    def test_voter_can_vote(self):
        self.authenticate(self.voter)

        res = self.client.post("/api/votes/", {
            "option": self.option.id
        })

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)

    def test_voter_cannot_vote_twice(self):
        self.authenticate(self.voter)

        self.client.post("/api/votes/", {"option": self.option.id})
        res = self.client.post("/api/votes/", {"option": self.option.id})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_guest_vote_disallowed_when_flag_false(self):
        self.poll.allow_guest_votes = False
        self.poll.save()

        res = self.client.post("/api/votes/", {"option": self.option.id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
