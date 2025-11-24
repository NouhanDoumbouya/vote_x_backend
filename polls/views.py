from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics
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
    SimpleUserSerializer,
)
from users.models import User


# --------------------------------------
# LIST + CREATE POLLS  (/api/polls/)
# --------------------------------------
class PollListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Poll.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        return PollCreateSerializer if self.request.method == "POST" else PollListSerializer

    def get_queryset(self):
        user = self.request.user

        base_qs = (
            Poll.objects.filter(is_active=True)
            .select_related("owner")
            .prefetch_related("options", "allowed_users")
        )

        # Guests → only public polls
        if not user.is_authenticated:
            return base_qs.filter(visibility="public")

        # Authenticated → public + ones they own or are allowed in
        return (
            base_qs.filter(
                Q(visibility="public")
                | Q(visibility="private", owner=user)
                | Q(visibility="restricted", allowed_users=user)
            )
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# --------------------------------------
# POLL DETAIL  (/api/polls/<pk>/)
# --------------------------------------
class PollDetailView(generics.RetrieveAPIView):
    serializer_class = PollDetailSerializer
    queryset = Poll.objects.select_related("owner").prefetch_related(
        "options", "allowed_users"
    )
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        poll = self.get_object()
        user = request.user

        # Public → always viewable
        if poll.visibility == "public":
            return super().get(request, *args, **kwargs)

        # Auth required for private/restricted
        if not user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=403)

        if poll.visibility == "private" and poll.owner != user:
            return Response({"detail": "Access denied."}, status=403)

        if poll.visibility == "restricted" and user not in poll.allowed_users.all():
            return Response({"detail": "Access restricted."}, status=403)

        return super().get(request, *args, **kwargs)
    
# --------------------------------------
# DELETE POLL  (/api/polls/<pk>/delete/)
# --------------------------------------
class PollDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        poll = get_object_or_404(Poll, pk=pk)

        if poll.owner != request.user:
            raise PermissionDenied("Only the poll owner can delete this poll.")

        poll.delete()
        return Response({"detail": "Poll deleted successfully."}, status=204)



# --------------------------------------
# OPTIONS LIST/CREATE  (/api/polls/<poll_id>/options/)
# --------------------------------------
class OptionListCreateView(generics.ListCreateAPIView):
    serializer_class = OptionSerializer

    def get_queryset(self):
        return Option.objects.filter(poll_id=self.kwargs["poll_id"])

    def perform_create(self, serializer):
        poll = Poll.objects.get(pk=self.kwargs["poll_id"])
        user = self.request.user

        if not user.is_authenticated or poll.owner != user:
            raise PermissionDenied("Only the poll owner can add options.")

        serializer.save(poll=poll)


# --------------------------------------
# SHARE LINK VIEW  (/api/polls/share/<share_id>/)
# --------------------------------------
class PollShareLinkView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, share_id):
        try:
            poll = Poll.objects.select_related("owner").prefetch_related(
                "options", "allowed_users"
            ).get(shareable_id=share_id)
        except Poll.DoesNotExist:
            return Response({"detail": "Invalid or expired link."}, status=404)

        user = request.user

        if poll.visibility == "public":
            return Response(
                PollDetailSerializer(poll, context={"request": request}).data
            )

        if poll.visibility == "private":
            if not user.is_authenticated or poll.owner != user:
                return Response({"detail": "This poll is private."}, status=403)

        if poll.visibility == "restricted":
            if not user.is_authenticated or user not in poll.allowed_users.all():
                return Response({"detail": "Access restricted."}, status=403)

        return Response(
            PollDetailSerializer(poll, context={"request": request}).data
        )


# --------------------------------------
# ALLOWED USERS VIEW  (/api/polls/<poll_id>/allowed-users/)
# --------------------------------------
class AllowedUsersView(APIView):
    """
    Manage restricted poll allowed_users:
      GET    → list allowed users
      POST   → add user by email
      DELETE → remove user by email
    """
    permission_classes = [IsAuthenticated]

    def get_poll(self, poll_id):
        return get_object_or_404(
            Poll.objects.prefetch_related("allowed_users"),
            pk=poll_id
        )

    def _check_owner(self, request, poll):
        if poll.owner != request.user:
            raise PermissionDenied("Only the poll owner can modify allowed users.")

    def get(self, request, poll_id):
        poll = self.get_poll(poll_id)
        self._check_owner(request, poll)

        serializer = SimpleUserSerializer(poll.allowed_users.all(), many=True)
        return Response(serializer.data)

    def post(self, request, poll_id):
        """
        Body:
        {
          "email": "user@example.com"
        }
        """
        poll = self.get_poll(poll_id)
        self._check_owner(request, poll)

        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        poll.allowed_users.add(user)
        serializer = SimpleUserSerializer(poll.allowed_users.all(), many=True)
        return Response(serializer.data)

    def delete(self, request, poll_id):
        """
        Body:
        {
          "email": "user@example.com"
        }
        """
        poll = self.get_poll(poll_id)
        self._check_owner(request, poll)

        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        poll.allowed_users.remove(user)
        serializer = SimpleUserSerializer(poll.allowed_users.all(), many=True)
        return Response(serializer.data)
