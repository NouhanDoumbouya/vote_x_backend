from django.db import models
from django.conf import settings
from polls.models import Option

User = settings.AUTH_USER_MODEL


class Vote(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="votes",
        null=True,       # allow guests (user = null)
        blank=True
    )

    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        related_name="votes"
    )

    # For guests only
    guest_ip = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Logged-in users: 1 vote per POLL
            models.UniqueConstraint(
                fields=["user", "option"],
                name="unique_user_vote_per_option",
                condition=models.Q(user__isnull=False),
            ),

            # Guests: 1 vote per POLL per IP
            models.UniqueConstraint(
                fields=["guest_ip", "option"],
                name="unique_guest_ip_vote_per_option",
                condition=models.Q(user__isnull=True),
            ),
        ]

    def __str__(self):
        voter = self.user if self.user else f"Guest({self.guest_ip})"
        return f"{voter} -> {self.option}"
