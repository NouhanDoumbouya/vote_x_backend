from rest_framework import serializers
from django.utils import timezone

from .models import Poll, Option
from votes.models import Vote
from users.models import User


# ---------------------------------------------------
# SIMPLE USER (for allowed_users)
# ---------------------------------------------------
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


# ---------------------------------------------------
# OPTION SERIALIZERS
# ---------------------------------------------------

class OptionSerializer(serializers.ModelSerializer):
    """Simple option without vote counts."""
    class Meta:
        model = Option
        fields = ["id", "text"]


class OptionWithVotesSerializer(serializers.ModelSerializer):
    """Option including vote count (for list/detail/results)."""
    votes = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ["id", "text", "votes"]

    def get_votes(self, obj):
        return Vote.objects.filter(option=obj).count()


# ---------------------------------------------------
# SHARED HELPERS
# ---------------------------------------------------

def _get_ends_in(obj: Poll) -> str:
    if not obj.expires_at:
        return "No deadline"

    remaining = obj.expires_at - timezone.now()
    if remaining.total_seconds() <= 0:
        return "Expired"

    days = remaining.days
    hours = remaining.seconds // 3600
    return f"{days}d {hours}h"


def _get_total_votes(obj: Poll) -> int:
    return Vote.objects.filter(option__poll=obj).count()


# ---------------------------------------------------
# POLL LIST SERIALIZER  (Home page)
# ---------------------------------------------------

class PollListSerializer(serializers.ModelSerializer):
    options = OptionWithVotesSerializer(many=True, read_only=True)
    total_votes = serializers.SerializerMethodField()
    ends_in = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    allowed_users = SimpleUserSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = [
            "id",
            "title",
            "description",
            "category",
            "created_at",
            "expires_at",
            "ends_in",
            "total_votes",
            "visibility",
            "shareable_id",
            "is_active",
            "allow_guest_votes",
            "is_owner",
            "allowed_users",
            "options",
        ]

    def get_total_votes(self, obj):
        return _get_total_votes(obj)

    def get_ends_in(self, obj):
        return _get_ends_in(obj)

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.owner_id == request.user.id


# ---------------------------------------------------
# POLL DETAIL SERIALIZER
# ---------------------------------------------------

class PollDetailSerializer(serializers.ModelSerializer):
    options = OptionWithVotesSerializer(many=True, read_only=True)
    total_votes = serializers.SerializerMethodField()
    ends_in = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    allowed_users = SimpleUserSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = [
            "id",
            "title",
            "description",
            "category",
            "created_at",
            "expires_at",
            "ends_in",
            "visibility",
            "allow_guest_votes",
            "shareable_id",
            "is_active",
            "is_owner",
            "allowed_users",
            "options",
            "total_votes",
        ]

    def get_total_votes(self, obj):
        return _get_total_votes(obj)

    def get_ends_in(self, obj):
        return _get_ends_in(obj)

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.owner_id == request.user.id


# ---------------------------------------------------
# POLL CREATE SERIALIZER
# ---------------------------------------------------

class PollCreateSerializer(serializers.ModelSerializer):
    # Frontend sends: ["Python", "Rust", "Go"]
    options = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
    )

    # NEW: frontend sends list of emails
    allowed_users = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=False,
        default=[]
    )

    class Meta:
        model = Poll
        fields = [
            "title",
            "description",
            "category",
            "expires_at",
            "visibility",
            "allow_guest_votes",
            "options",
            "allowed_users",   # NEW
        ]

    def create(self, validated_data):
        options_data = validated_data.pop("options")
        allowed_user_emails = validated_data.pop("allowed_users", [])

        poll = Poll.objects.create(**validated_data)

        # Create options
        for text in options_data:
            Option.objects.create(poll=poll, text=text)

        # If poll is restricted — attach allowed users
        if poll.visibility == "restricted" and allowed_user_emails:
            users = User.objects.filter(email__in=allowed_user_emails)

            # Important: add them to the M2M
            poll.allowed_users.add(*users)

        return poll

