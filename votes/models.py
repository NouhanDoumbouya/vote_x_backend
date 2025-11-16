from django.db import models
from django.conf import settings
from polls.models import Option

User = settings.AUTH_USER_MODEL

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="votes")
    guest_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "option", "guest_ip")  # prevent duplicate votes

    def __str__(self):
        return f"{self.user} -> {self.option}"
