from rest_framework import serializers
from django.utils import timezone
from .models import Poll, Option


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text"]


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    created_by = serializers.ReadOnlyField(source="created_by.id")
    is_expired = serializers.SerializerMethodField()
    # FIX: allow expires_at to be null or omitted
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

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
            "allow_guest_votes",
            "is_expired",
            "options",
        ]

    def get_is_expired(self, obj):
        return obj.is_expired

    def validate_expires_at(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")
        return value
