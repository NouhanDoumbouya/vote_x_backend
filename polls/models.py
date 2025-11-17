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

    CATEGORY_CHOICES = [
        ("general", "General"),
        ("technology", "Technology"),
        ("education", "Education"),
        ("events", "Events"),
        ("sports", "Sports"),
        ("entertainment", "Entertainment"),
        ("other", "Other"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="polls"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="general"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    allow_guest_votes = models.BooleanField(default=False)

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="public"
    )

    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="allowed_polls",
        blank=True
    )

    shareable_id = models.CharField(
        max_length=32,
        unique=True,
        default=lambda: uuid.uuid4().hex
    )

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
