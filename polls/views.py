from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Poll, Option
from .serializers import PollSerializer, OptionSerializer
from users.permissions import IsAdminUserRole
import django.db.models as models

class PollListCreateView(generics.ListCreateAPIView):
    serializer_class = PollSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAdminUserRole()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        now = timezone.now()
        return Poll.objects.filter(is_active=True).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PollDetailView(generics.RetrieveDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [permissions.IsAuthenticated(), IsAdminUserRole()]
        return [permissions.AllowAny()]


class OptionListCreateView(generics.ListCreateAPIView):
    serializer_class = OptionSerializer

    def get_queryset(self):
        poll_id = self.kwargs["poll_id"]
        return Option.objects.filter(poll_id=poll_id)

    def perform_create(self, serializer):
        poll_id = self.kwargs["poll_id"]
        poll = Poll.objects.get(pk=poll_id)

        if not (self.request.user.is_authenticated and self.request.user.role == "admin"):
            raise PermissionDenied("Only admin users can add options.")

        serializer.save(poll=poll)
