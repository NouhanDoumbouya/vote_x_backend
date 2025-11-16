from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Roles Definition
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('voter', 'Voter'),
    )

    # Overide the default username field to email
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='voter')
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'    # login using email
    REQUIRED_FIELDS = ['username'] #required when creating superuser

    def __str__(self):
        return self.email
