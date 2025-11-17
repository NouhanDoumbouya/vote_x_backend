# polls/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Poll, Option
from votes.models import Vote


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
# POLL LIST SERIALIZER  (Home page)
# ---------------------------------------------------

class PollListSerializer(serializers.ModelSerializer):
    options = OptionWithVotesSerializer(many=True, read_only=True)
    total_votes = serializers.SerializerMethodField()
    ends_in = serializers.SerializerMethodField()

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
            "options",
        ]

    def get_total_votes(self, obj):
        return Vote.objects.filter(option__poll=obj).count()

    def get_ends_in(self, obj):
        if not obj.expires_at:
            return "No deadline"

        remaining = obj.expires_at - timezone.now()
        if remaining.total_seconds() <= 0:
            return "Expired"

        days = remaining.days
        hours = remaining.seconds // 3600
        return f"{days}d {hours}h"


# ---------------------------------------------------
# POLL DETAIL SERIALIZER
# ---------------------------------------------------

class PollDetailSerializer(serializers.ModelSerializer):
    options = OptionWithVotesSerializer(many=True, read_only=True)
    total_votes = serializers.SerializerMethodField()
    ends_in = serializers.SerializerMethodField()

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
            "options",
            "total_votes",
        ]

    def get_total_votes(self, obj):
        return Vote.objects.filter(option__poll=obj).count()

    def get_ends_in(self, obj):
        if not obj.expires_at:
            return "No deadline"

        remaining = obj.expires_at - timezone.now()
        if remaining.total_seconds() <= 0:
            return "Expired"

        days = remaining.days
        hours = remaining.seconds // 3600
        return f"{days}d {hours}h"


# ---------------------------------------------------
# POLL CREATE SERIALIZER
# ---------------------------------------------------

class PollCreateSerializer(serializers.ModelSerializer):
    # Frontend sends: ["Python", "Rust", "Go"]
    options = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
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
        ]

    def create(self, validated_data):
        options_data = validated_data.pop("options")
        poll = Poll.objects.create(**validated_data)

        for text in options_data:
            Option.objects.create(poll=poll, text=text)

        return poll
