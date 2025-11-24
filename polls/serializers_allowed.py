from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Poll

User = get_user_model()


class AllowedUsersUpdateSerializer(serializers.Serializer):
    allowed_users = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )

    def validate_allowed_users(self, ids):
        # Ensure all IDs exist
        qs = User.objects.filter(id__in=ids)
        if qs.count() != len(ids):
            raise serializers.ValidationError("One or more user IDs are invalid.")
        return ids

    def update(self, instance, validated_data):
        user_ids = validated_data["allowed_users"]
        instance.allowed_users.set(user_ids)
        instance.save()
        return instance
