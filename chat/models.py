from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """Conversa entre 2+ usuários (aqui usada tipicamente 1-a-1)."""

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        names = ", ".join(self.participants.values_list("username", flat=True))
        return f"Conversa #{self.pk} ({names})"

    @property
    def last_message(self):
        return self.messages.order_by("-created_at").first()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Mensagem de {self.sender.username} em #{self.conversation_id}"
