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

        # 1. Poll must be active and not expired
        if poll.is_expired:
            raise serializers.ValidationError("This poll has expired.")
        if not poll.is_active:
            raise serializers.ValidationError("This poll is no longer active.")

        # 2. Authenticated user voting logic
        if request.user.is_authenticated:
            if Vote.objects.filter(user=request.user, option__poll=poll).exists():
                raise serializers.ValidationError("You already voted on this poll.")
            return attrs

        # 3. Guest voting not allowed
        if not poll.allow_guest_votes:
            raise serializers.ValidationError("Guest voting is not allowed for this poll.")

        # 4. Guest voting logic → validate IP
        guest_ip = get_client_ip(request)

        if Vote.objects.filter(guest_ip=guest_ip, option__poll=poll).exists():
            raise serializers.ValidationError("Guest already voted on this poll.")
        
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

class PollResultOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    vote_count = serializers.IntegerField()

class PollResultsSerializer(serializers.Serializer):
    poll_id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    total_votes = serializers.IntegerField()
    options = PollResultOptionSerializer(many=True)