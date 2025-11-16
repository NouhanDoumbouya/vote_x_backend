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
        poll = Poll.objects.get(pk=poll_id)
        options = poll.options.annotate(vote_count=Count("votes")).values(
            "id", "text", "vote_count"
        )
        total_votes = Vote.objects.filter(option__poll=poll).count()

        return Response({
            "poll_id": poll.id,
            "title": poll.title,
            "total_votes": total_votes,
            "options": list(options),
        })
