from rest_framework import serializers

class ChatRequestSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=255)
    query = serializers.CharField()
