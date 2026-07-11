import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Conecta em: ws://<host>/ws/chat/<conversation_id>/?token=<jwt_access_token>

    Mensagens trocadas (JSON):
      Cliente -> Servidor: {"content": "oi, tudo bem?"}
      Servidor -> Cliente: {"id": 12, "content": "...", "sender": "fernando",
                             "created_at": "...", "conversation": 3}
    """

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"chat_{self.conversation_id}"
        user = self.scope.get("user")

        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        allowed = await self.user_in_conversation(user.id, self.conversation_id)
        if not allowed:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = (data.get("content") or "").strip()
        if not content:
            return

        user = self.scope["user"]
        message = await self.save_message(user.id, self.conversation_id, content)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": {
                    "id": message.id,
                    "content": message.content,
                    "sender": user.username,
                    "sender_id": user.id,
                    "conversation": int(self.conversation_id),
                    "created_at": message.created_at.isoformat(),
                },
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def user_in_conversation(self, user_id, conversation_id):
        return Conversation.objects.filter(pk=conversation_id, participants__id=user_id).exists()

    @database_sync_to_async
    def save_message(self, user_id, conversation_id, content):
        return Message.objects.create(
            conversation_id=conversation_id, sender_id=user_id, content=content
        )
