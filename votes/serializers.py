from rest_framework import serializers
from django.utils import timezone
from core.utils import get_client_ip
from .models import Vote

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["id", "option", "created_at"]

    def validate(self, attrs):
        request = self.context["request"]
        option = attrs["option"]
        poll = option.poll

        # Poll must be active
        if poll.is_expired:
            raise serializers.ValidationError("This poll has expired.")

        # -------- VISIBILITY RULES ----------
        if poll.visibility != "public":

            if not request.user.is_authenticated:
                raise serializers.ValidationError("Login required to vote.")

            if poll.visibility == "private" and poll.owner != request.user:
                raise serializers.ValidationError("You cannot vote on this poll.")

            if poll.visibility == "restricted" and request.user not in poll.allowed_users.all():
                raise serializers.ValidationError("You are not allowed to vote here.")

        # -------- GUEST VOTING ----------
        if not request.user.is_authenticated:
            if not poll.allow_guest_votes:
                raise serializers.ValidationError("Guest voting disabled.")

            ip = get_client_ip(request)
            if Vote.objects.filter(option__poll=poll, guest_ip=ip).exists():
                raise serializers.ValidationError("Guest already voted.")

            return attrs

        # -------- USER VOTING ----------
        if Vote.objects.filter(option__poll=poll, user=request.user).exists():
            raise serializers.ValidationError("You already voted.")

        return attrs


    def create(self, validated_data):
        request = self.context["request"]
        option = validated_data["option"]

        # Authenticated user
        if request.user.is_authenticated:
            return Vote.objects.create(
                user=request.user,
                option=option
            )

        # Guest user
        guest_ip = get_client_ip(request)
        return Vote.objects.create(
            guest_ip=guest_ip,
            option=option
        )