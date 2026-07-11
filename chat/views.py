from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageSerializer,
)


class ConversationListCreateView(APIView):
    """Lista as conversas do usuário logado, ou inicia uma nova."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        conversations = request.user.conversations.all()
        data = ConversationSerializer(conversations, many=True, context={"request": request}).data
        return Response(data)

    def post(self, request):
        serializer = ConversationCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data
        )


class MessageListCreateView(generics.ListCreateAPIView):
    """
    Histórico de mensagens de uma conversa (REST) — útil para carregar o
    histórico ao abrir o chat. O envio em tempo real acontece via WebSocket
    (veja chat/consumers.py), mas este endpoint também aceita POST como
    fallback (ex.: quando o WebSocket não está disponível).
    """

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_conversation(self):
        return Conversation.objects.filter(
            pk=self.kwargs["pk"], participants=self.request.user
        ).first()

    def get_queryset(self):
        conversation = self.get_conversation()
        if not conversation:
            return Message.objects.none()
        return conversation.messages.select_related("sender")

    def perform_create(self, serializer):
        conversation = self.get_conversation()
        serializer.save(sender=self.request.user, conversation=conversation)
