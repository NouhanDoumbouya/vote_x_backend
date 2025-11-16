from rest_framework import generics, permissions
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import Poll, Option
from .serializers import PollSerializer, OptionSerializer
from users.permissions import IsAdmin


class PollListCreateView(generics.ListCreateAPIView):
    serializer_class = PollSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        now = timezone.now()

        qs = (
            Poll.objects
            .filter(is_active=True)
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
            .select_related("created_by")
            .prefetch_related("options")
            .order_by("-created_at")
        )

        # ?search=...
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PollDetailView(generics.RetrieveDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdmin()]
        return [permissions.AllowAny()]


class OptionListCreateView(generics.ListCreateAPIView):
    serializer_class = OptionSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        poll_id = self.kwargs["poll_id"]
        return Option.objects.filter(poll_id=poll_id)

    def perform_create(self, serializer):
        poll_id = self.kwargs["poll_id"]
        poll = Poll.objects.get(pk=poll_id)
        serializer.save(poll=poll)
