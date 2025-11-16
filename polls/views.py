from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import Poll, Option
from .serializers import PollSerializer, OptionSerializer
from users.permissions import IsAdminUserRole
import django.db.models as models
from django.db.models import Q


class PollListCreateView(generics.ListCreateAPIView):
    serializer_class = PollSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsAdminUserRole()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        now = timezone.now()

        qs = (
            Poll.objects
            .filter(is_active=True)
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
            .select_related("created_by")          # optimization
            .prefetch_related("options")           # optimization
            .order_by("-created_at")
        )

        # simple search filter ?search=...
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
