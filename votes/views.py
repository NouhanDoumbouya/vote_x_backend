from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Count
from polls.models import Poll
from .models import Vote
from .serializers import VoteSerializer


class VoteCreateView(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]


class PollResultsView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, poll_id):
        # Fetch poll optimized
        poll = (
            Poll.objects
            .select_related("created_by")
            .prefetch_related("options")
            .get(pk=poll_id)
        )

        # Aggregate votes per option
        options = poll.options.annotate(
            vote_count=Count("votes")
        ).values("id", "text", "vote_count")

        # Total votes for this poll
        total_votes = Vote.objects.filter(option__poll=poll).count()

        return Response({
            "poll_id": poll.id,
            "title": poll.title,
            "description": poll.description,
            "total_votes": total_votes,
            "options": list(options),
        })

