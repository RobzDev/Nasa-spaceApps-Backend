from django.contrib import admin
from .models import ChatSession, ChatMessage

class ChatMessageInline(admin.TabularInline):
    """Permite ver y editar mensajes directamente desde la vista de la sesión de chat."""
    model = ChatMessage
    extra = 1
    readonly_fields = ('sender', 'message_text', 'timestamp')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Configuración del admin para las sesiones de chat."""
    list_display = ('id', 'user', 'start_time')
    list_filter = ('user', 'start_time')
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Configuración del admin para los mensajes."""
    list_display = ('id', 'session', 'sender', 'timestamp')
    list_filter = ('sender',)
