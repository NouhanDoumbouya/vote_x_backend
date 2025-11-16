from rest_framework import serializers
from .models import Vote

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["id", "option", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        option = attrs["option"]

        # Prevent duplicate votes
        if Vote.objects.filter(user=user, option=option).exists():
            raise serializers.ValidationError("You have already voted for this option.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return Vote.objects.create(user=user, **validated_data)
