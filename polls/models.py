from django.db import models
from django.conf import settings
from django.utils import timezone

# Import User model
User = settings.AUTH_USER_MODEL

# Poll model
class Poll(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="polls"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    allow_guest_votes = models.BooleanField(default=True)


    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        return self.expires_at and self.expires_at < timezone.now()
    
    @property
    def is_current(self):
        return self.is_active and not self.is_expired



class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.poll.title} - {self.text}"
