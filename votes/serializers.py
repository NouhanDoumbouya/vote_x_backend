from core.utils import get_client_ip
from polls.models import Option
from rest_framework import serializers
from .models import Vote

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["id", "option", "created_at"]

def validate(self, attrs):
    request = self.context["request"]
    option = attrs["option"]
    poll = option.poll  # shortcut

    # If user is authenticated
    if request.user.is_authenticated:
        if Vote.objects.filter(user=request.user, option=option).exists():
            raise serializers.ValidationError("You already voted on this option.")
        return attrs

    # If user is a guest but guest voting is disabled
    if not poll.allow_guest_votes:
        raise serializers.ValidationError("Guest voting is not allowed for this poll.")

    # Guest voting allowed → validate IP duplicate
    guest_ip = get_client_ip(request)

    if Vote.objects.filter(
        guest_ip=guest_ip,
        option__poll=poll
    ).exists():
        raise serializers.ValidationError("Guest already voted on this poll.")

    return attrs

    def create(self, validated_data):
        request = self.context["request"]
        option = validated_data["option"]

        if request.user.is_authenticated:
            return Vote.objects.create(user=request.user, option=option)

        # guest logic
        guest_ip = get_client_ip(request)
        return Vote.objects.create(guest_ip=guest_ip, option=option)
