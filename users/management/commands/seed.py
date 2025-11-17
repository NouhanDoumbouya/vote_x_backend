from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import User
from polls.models import Poll, Option

class Command(BaseCommand):
    help = "Seed database with initial data"

    def handle(self, *args, **kwargs):

        # Skip during tests
        if getattr(settings, "TESTING", False):
            self.stdout.write(self.style.WARNING("Skipping seed during tests."))
            return

        # -------------------------
        # USERS
        # -------------------------
        admin, _ = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "username": "admin",
                "role": "admin",
            }
        )
        admin.set_password("admin123")
        admin.save()

        voter, _ = User.objects.get_or_create(
            email="voter@example.com",
            defaults={
                "username": "voter",
                "role": "voter",
            }
        )
        voter.set_password("voter123")
        voter.save()

        # -------------------------
        # POLL
        # -------------------------
        poll, _ = Poll.objects.get_or_create(
            title="Best Programming Language",
            description="Vote for your favorite language",
            owner=admin,                      # 🔥 FIXED HERE
            visibility="public",
            allow_guest_votes=True,
            category="Technology"
        )

        # -------------------------
        # OPTIONS
        # -------------------------
        options = ["Python", "Rust", "Go", "JavaScript"]

        for text in options:
            Option.objects.get_or_create(poll=poll, text=text)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
