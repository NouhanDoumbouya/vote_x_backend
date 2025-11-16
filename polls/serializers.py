from rest_framework import serializers
from .models import Poll, Option

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "poll"]


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    created_by = serializers.ReadOnlyField(source="created_by.id")

    class Meta:
        model = Poll
        fields = [
            "id",
            "title",
            "description",
            "created_by",
            "created_at",
            "expires_at",
            "is_active",
            "allow_guest_votes", # Decide whether to include guest votes
            "options",
        ]
