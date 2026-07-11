from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import UserPublicSerializer

from .models import Conversation, Message

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender = UserPublicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ("id", "conversation", "sender", "content", "created_at", "read")
        read_only_fields = ("id", "sender", "created_at", "read", "conversation")


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserPublicSerializer(many=True, read_only=True)
    last_message = MessageSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ("id", "participants", "last_message", "created_at")


class ConversationCreateSerializer(serializers.Serializer):
    """Cria (ou reaproveita) uma conversa 1-a-1 com outro usuário pelo username."""

    username = serializers.CharField()

    def validate_username(self, value):
        request = self.context["request"]
        if value == request.user.username:
            raise serializers.ValidationError("Você não pode iniciar uma conversa consigo mesmo.")
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Usuário não encontrado.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        other = User.objects.get(username=validated_data["username"])

        existing = (
            Conversation.objects.filter(participants=request.user)
            .filter(participants=other)
            .first()
        )
        if existing:
            return existing

        conversation = Conversation.objects.create()
        conversation.participants.set([request.user, other])
        return conversation
