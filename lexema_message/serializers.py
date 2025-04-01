from rest_framework import serializers

from lexema_message.models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    recipient = serializers.StringRelatedField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'sender', 'timestamp', 'is_read']

    def create(self, validated_data):
        message = Message.objects.create(**validated_data)
        message.create_notification()  # Создаём уведомление
        return message