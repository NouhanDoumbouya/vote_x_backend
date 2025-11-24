from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count

from polls.models import Poll
from .models import Vote
from .serializers import VoteSerializer
from .serializers_results import PollResultsSerializer
from core.utils import get_client_ip


# ---------------------------------------------
# CREATE VOTE  (/api/votes/)
# ---------------------------------------------
class VoteCreateView(generics.CreateAPIView):
    serializer_class = VoteSerializer

    def get_permissions(self):
        # Guests and authenticated users allowed (handled in serializer)
        return [permissions.AllowAny()]


# ---------------------------------------------
# POLL RESULTS  (/api/votes/results/<poll_id>/)
# ---------------------------------------------
class PollResultsView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PollResultsSerializer

    def get(self, request, poll_id):
        poll = (
            Poll.objects
            .select_related("owner")
            .prefetch_related("options")
            .get(pk=poll_id)
        )

        # Count votes per option
        options = poll.options.annotate(
            vote_count=Count("votes")
        ).values("id", "text", "vote_count")

        total_votes = Vote.objects.filter(option__poll=poll).count()

        data = {
            "poll_id": poll.id,
            "title": poll.title,
            "description": poll.description or "",
            "total_votes": total_votes,
            "options": list(options),
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


# ---------------------------------------------
# USER (OR GUEST) VOTE CHECK  (/api/votes/me/<poll_id>/)
# ---------------------------------------------
class UserVoteView(APIView):
    """
    Returns the option ID the current user or guest voted for.
    {
        "voted_option_id": 12
    }
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, poll_id):
        user = request.user
        ip = get_client_ip(request)

        # Logged-in user
        if user.is_authenticated:
            vote = Vote.objects.filter(
                user=user,
                option__poll_id=poll_id
            ).first()

        # Guest user
        else:
            vote = Vote.objects.filter(
                guest_ip=ip,
                option__poll_id=poll_id
            ).first()

        if not vote:
            return Response({"voted_option_id": None})

        return Response({"voted_option_id": vote.option.id})
