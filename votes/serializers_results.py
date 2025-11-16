from rest_framework import serializers

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
