from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from polls.models import Poll, Option
from votes.models import Vote


class TestVotes(APITestCase):

    def setUp(self):
        # Admin user (just a normal user with role=admin)
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
        )

        # Normal voter user
        self.voter = User.objects.create_user(
            username="voter",
            email="voter@example.com",
            password="voter123",
            role="voter",
        )

        # Poll now uses `owner` instead of `created_by`
        self.poll = Poll.objects.create(
            owner=self.admin,
            title="Favorite Language",
            description="Choose your favorite programming language",
            allow_guest_votes=True,
            visibility="public",
        )

        self.option = Option.objects.create(
            poll=self.poll,
            text="Python",
        )

    def authenticate(self, user: User):
        """Helper: log in via JWT login endpoint and attach Bearer token."""
        res = self.client.post(
            "/api/auth/login/",
            {
                "email": user.email,
                "password": "admin123" if user.role == "admin" else "voter123",
            },
        )
        # Make sure login is actually working
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_voter_can_vote(self):
        """Authenticated voter can cast a vote on a poll option."""
        self.authenticate(self.voter)

        res = self.client.post("/api/votes/", {"option": self.option.id})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        self.assertEqual(Vote.objects.count(), 1)

    def test_voter_cannot_vote_twice_on_same_poll(self):
        """Authenticated user cannot vote twice on the same poll."""
        self.authenticate(self.voter)

        # First vote OK
        first = self.client.post("/api/votes/", {"option": self.option.id})
        self.assertEqual(first.status_code, status.HTTP_201_CREATED, first.data)

        # Second vote on same poll should fail
        second = self.client.post("/api/votes/", {"option": self.option.id})
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST, second.data)

    def test_guest_cannot_vote_when_guest_disabled(self):
        """
        When allow_guest_votes=False, unauthenticated (guest) users
        are blocked from voting.
        """
        self.poll.allow_guest_votes = False
        self.poll.save()

        res = self.client.post("/api/votes/", {"option": self.option.id})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, res.data)

    def test_guest_can_vote_once_when_guest_enabled(self):
        """
        When allow_guest_votes=True, a guest can vote once per poll.
        Second attempt from same IP should be rejected.
        """
        # First guest vote
        first = self.client.post("/api/votes/", {"option": self.option.id})
        self.assertEqual(first.status_code, status.HTTP_201_CREATED, first.data)
        self.assertEqual(Vote.objects.count(), 1)

        # Second guest vote from same IP (DRF test client keeps same REMOTE_ADDR)
        second = self.client.post("/api/votes/", {"option": self.option.id})
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST, second.data)
        self.assertEqual(Vote.objects.count(), 1)
