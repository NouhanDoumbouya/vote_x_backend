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

        # ------------------------------
        # 1. Ensure poll is active
        # ------------------------------
        if poll.is_expired:
            raise serializers.ValidationError("This poll has expired.")

        # ------------------------------
        # 2. Poll visibility rules
        # ------------------------------
        if poll.visibility != "public":

            if not request.user.is_authenticated:
                raise serializers.ValidationError("Login required to vote.")

            if poll.visibility == "private" and poll.owner != request.user:
                raise serializers.ValidationError("You cannot vote on this poll.")

            if poll.visibility == "restricted" and request.user not in poll.allowed_users.all():
                raise serializers.ValidationError("You are not allowed to vote here.")

        # ------------------------------
        # 3. Guest voting
        # ------------------------------
        if not request.user.is_authenticated:
            if not poll.allow_guest_votes:
                raise serializers.ValidationError("Guest voting disabled.")

            guest_ip = get_client_ip(request)
            # Check guest already voted on THIS POLL (not per option)
            if Vote.objects.filter(option__poll=poll, guest_ip=guest_ip).exists():
                raise serializers.ValidationError("Guest already voted.")

            return attrs  # Guest is allowed

        # ------------------------------
        # 4. Authenticated user voting
        # ------------------------------
        user = request.user

        # Check if user voted in THIS POLL already
        if Vote.objects.filter(option__poll=poll, user=user).exists():
            raise serializers.ValidationError("You already voted.")

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        option = validated_data["option"]

        # ------------------------------
        # Logged-in user
        # ------------------------------
        if request.user.is_authenticated:
            return Vote.objects.create(
                user=request.user,
                option=option
            )

        # ------------------------------
        # Guest
        # ------------------------------
        guest_ip = get_client_ip(request)
        return Vote.objects.create(
            guest_ip=guest_ip,
            option=option
        )
