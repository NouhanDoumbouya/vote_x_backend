from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Count
from polls.models import Poll
from users.permissions import IsVoter
from .models import Vote
from .serializers import VoteSerializer
from .serializers_results import PollResultsSerializer


class VoteCreateView(generics.CreateAPIView):
    serializer_class = VoteSerializer

    def get_permissions(self):
        """
        Allow both authenticated voters and guests to vote.
        But handle permissions in serializer validation.
        Whether guest voting is allowed is poll-specific.
        """
        return [permissions.AllowAny()]



class PollResultsView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PollResultsSerializer   # <-- REQUIRED

    def get(self, request, poll_id):
        poll = (
            Poll.objects
            .select_related("created_by")
            .prefetch_related("options")
            .get(pk=poll_id)
        )

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

        return Response(self.get_serializer(data).data)

