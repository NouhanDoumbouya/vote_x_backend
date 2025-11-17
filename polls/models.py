from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Poll(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
        ("restricted", "Restricted"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="polls",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Optional category for frontend filters
    category = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    allow_guest_votes = models.BooleanField(default=False)

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="public",
    )

    # For restricted polls (only specific users can see/vote)
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="allowed_polls",
        blank=True,
    )

    # Stable shareable link ID
    shareable_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )


    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class Option(models.Model):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name="options",
    )
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.poll.title} - {self.text}"
