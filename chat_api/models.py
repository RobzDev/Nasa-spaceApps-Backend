from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    """
    Representa una conversación completa o una sesión de chat.
    Cada sesión pertenece a un usuario.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    start_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Muestra una representación legible en el admin de Django
        return f"Chat con {self.user.username} iniciado a las {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class ChatMessage(models.Model):
    """
    Representa un único mensaje dentro de una ChatSession.
    """
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.sender}] {self.message_text[:50]}..."
