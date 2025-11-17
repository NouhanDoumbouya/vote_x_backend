from django.utils import timezone
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from .models import Poll, Option
from .serializers import (
    PollListSerializer,
    PollDetailSerializer,
    PollCreateSerializer,
    OptionSerializer,
)


# --------------------------------------
# LIST + CREATE POLLS  (/api/polls/)
# --------------------------------------
class PollListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]  # override in get_permissions
    queryset = Poll.objects.filter(is_active=True).select_related("owner").prefetch_related("options")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PollCreateSerializer
        return PollListSerializer

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        base_qs = Poll.objects.filter(
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        ).select_related("owner").prefetch_related("options")

        # Guests -> only public
        if not user.is_authenticated:
            return base_qs.filter(visibility="public")

        # Authenticated -> public + private they own + restricted where they're allowed
        return base_qs.filter(
            Q(visibility="public") |
            Q(visibility="private", owner=user) |
            Q(visibility="restricted", allowed_users=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# --------------------------------------
# POLL DETAIL  (/api/polls/<pk>/)
# --------------------------------------
class PollDetailView(generics.RetrieveAPIView):
    serializer_class = PollDetailSerializer
    queryset = Poll.objects.all()
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        poll = self.get_object()
        user = request.user

        # Public: always viewable
        if poll.visibility == "public":
            return super().get(request, *args, **kwargs)

        # Auth required beyond this point
        if not user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=403)

        # Private: only owner
        if poll.visibility == "private" and poll.owner != user:
            return Response({"detail": "Access denied."}, status=403)

        # Restricted: must be in allowed_users
        if poll.visibility == "restricted" and user not in poll.allowed_users.all():
            return Response({"detail": "Access restricted."}, status=403)

        return super().get(request, *args, **kwargs)


# --------------------------------------
# OPTIONS LIST/CREATE  (/api/polls/<poll_id>/options/)
# --------------------------------------
class OptionListCreateView(generics.ListCreateAPIView):
    serializer_class = OptionSerializer

    def get_queryset(self):
        poll_id = self.kwargs["poll_id"]
        return Option.objects.filter(poll_id=poll_id)

    def perform_create(self, serializer):
        poll_id = self.kwargs["poll_id"]
        poll = Poll.objects.get(pk=poll_id)

        # Only owner can add options
        user = self.request.user
        if not user.is_authenticated or poll.owner != user:
            raise PermissionDenied("Only the poll owner can add options.")

        serializer.save(poll=poll)


# --------------------------------------
# SHAREABLE LINK VIEW (/api/polls/share/<share_id>/)
# --------------------------------------
class PollShareLinkView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, share_id):
        try:
            poll = Poll.objects.get(shareable_id=share_id)
        except Poll.DoesNotExist:
            return Response({"detail": "Invalid or expired link."}, status=404)

        user = request.user

        # Public polls via link: always visible
        if poll.visibility == "public":
            serializer = PollDetailSerializer(poll, context={"request": request})
            return Response(serializer.data)

        # Private: only owner
        if poll.visibility == "private":
            if not user.is_authenticated or poll.owner != user:
                return Response({"detail": "This poll is private."}, status=403)

        # Restricted: must be allowed
        if poll.visibility == "restricted":
            if not user.is_authenticated or user not in poll.allowed_users.all():
                return Response({"detail": "Access restricted for this poll."}, status=403)

        serializer = PollDetailSerializer(poll, context={"request": request})
        return Response(serializer.data)
