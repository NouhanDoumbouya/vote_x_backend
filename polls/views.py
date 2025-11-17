# polls/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .models import Poll, Option
from .serializers import (
    PollListSerializer,
    PollDetailSerializer,
    PollCreateSerializer,
    OptionSerializer,
)
from votes.models import Vote


# --------------------------------------
# Helper: visibility rules
# --------------------------------------
def can_view_poll(request, poll):
    user = request.user if request.user.is_authenticated else None

    if poll.visibility == "public":
        return True

    if poll.visibility == "private":
        return user == poll.owner

    if poll.visibility == "restricted":
        return user and (user == poll.owner or user in poll.allowed_users.all())

    return False



# --------------------------------------
# LIST POLLS (for home page)
# --------------------------------------
class PollListView(generics.ListAPIView):
    serializer_class = PollListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Poll.objects.filter(visibility="public", is_active=True)

        return Poll.objects.filter(
            Q(visibility="public") |
            Q(visibility="private", owner=user) |
            Q(visibility="restricted", allowed_users=user)
        ).distinct()



# --------------------------------------
# CREATE POLL (any authenticated user)
# --------------------------------------
class PollCreateView(generics.CreateAPIView):
    serializer_class = PollCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



# --------------------------------------
# POLL DETAIL VIEW (with visibility rules)
# --------------------------------------
class PollDetailView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollDetailSerializer
    lookup_url_kwarg = "poll_id"
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        poll = self.get_object()

        if not can_view_poll(request, poll):
            return Response({"detail": "Not authorized to view this poll"}, status=403)

        return super().get(request, *args, **kwargs)



# --------------------------------------
# OPTIONS LIST / CREATE (owner only)
# --------------------------------------
class OptionListCreateView(generics.ListCreateAPIView):
    serializer_class = OptionSerializer

    def get_queryset(self):
        return Option.objects.filter(poll_id=self.kwargs["poll_id"])

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        poll = Poll.objects.get(id=self.kwargs["poll_id"])
        if poll.owner != self.request.user:
            raise PermissionDenied("Only the poll owner can add options.")
        serializer.save(poll=poll)



# --------------------------------------
# VOTE ENDPOINT (supports guests)
# --------------------------------------
class VoteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, poll_id):
        poll = get_object_or_404(Poll, id=poll_id)
        
        if not can_view_poll(request, poll):
            return Response({"detail": "Access denied"}, status=403)

        option_id = request.data.get("option_id")
        option = get_object_or_404(Option, id=option_id, poll=poll)

        # Authenticated
        if request.user.is_authenticated:
            Vote.objects.update_or_create(
                user=request.user,
                poll=poll,
                defaults={"option": option},
            )
            return Response({"message": "Vote recorded"})

        # Guest user
        if not poll.allow_guest_votes:
            return Response({"detail": "Login required"}, status=403)

        guest_ip = request.META.get("REMOTE_ADDR")

        Vote.objects.update_or_create(
            guest_ip=guest_ip,
            poll=poll,
            defaults={"option": option},
        )
        return Response({"message": "Vote recorded"})


# --------------------------------------
# RESULTS ENDPOINT
# --------------------------------------
class PollResultsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, poll_id):
        poll = get_object_or_404(Poll, id=poll_id)

        if not can_view_poll(request, poll):
            return Response({"detail": "Access denied"}, status=403)

        options = poll.options.all()
        total_votes = Vote.objects.filter(poll=poll).count()

        results = {
            "poll_id": poll.id,
            "title": poll.title,
            "description": poll.description,
            "total_votes": total_votes,
            "options": [
                {
                    "id": opt.id,
                    "text": opt.text,
                    "vote_count": Vote.objects.filter(option=opt).count(),
                }
                for opt in options
            ],
        }

        return Response(results)



# --------------------------------------
# SHAREABLE LINK VIEW
# --------------------------------------
class PollShareLinkView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, share_id):
        poll = get_object_or_404(Poll, shareable_id=share_id)

        if not can_view_poll(request, poll):
            return Response({"detail": "Access denied"}, status=403)

        return Response(PollDetailSerializer(poll).data)
