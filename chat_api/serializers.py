from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage

class UserSerializer(serializers.ModelSerializer):
    """Serializer para registrar nuevos usuarios."""
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Usa el método create_user para hashear la contraseña correctamente
        user = User.objects.create_user(**validated_data)
        return user

class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer para mostrar mensajes individuales."""
    class Meta:
        model = ChatMessage
        fields = ('id', 'sender', 'message_text', 'timestamp')
        read_only_fields = ('id', 'sender', 'timestamp') # Estos campos se asignan en el backend

class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer para listar sesiones de chat."""
    class Meta:
        model = ChatSession
        fields = ('id', 'start_time')

class ChatSessionDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver el detalle (con mensajes) de una sesión de chat."""
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ('id', 'user', 'start_time', 'messages')
        read_only_fields = ('user',)