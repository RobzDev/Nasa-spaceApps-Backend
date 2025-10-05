from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatSession, ChatMessage
from .serializers import (
    UserSerializer, 
    ChatSessionSerializer, 
    ChatSessionDetailSerializer,
    ChatMessageSerializer
)

# Suponiendo que tu servicio RAG está en 'rag_app/services.py'
# ¡Asegúrate de que la ruta de importación sea correcta para tu proyecto!
from api.services import rag_service 

# --- Vistas para Usuarios y Autenticación ---

# --- LÍNEA CORREGIDA ---
# Cambiamos el nombre de 'UserCreate' a 'UserCreateView' para que coincida con urls.py
class UserCreateView(generics.CreateAPIView):
    """Vista para que nuevos usuarios se registren."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Cualquiera puede registrarse

# --- Vistas para Gestionar Sesiones de Chat ---

class ChatSessionListView(generics.ListCreateAPIView):
    """Vista para listar las sesiones de chat de un usuario o crear una nueva."""
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Devuelve solo las sesiones del usuario que hace la petición
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Asigna automáticamente el usuario actual al crear una sesión
        serializer.save(user=self.request.user)

class ChatSessionDetailView(generics.RetrieveAPIView):
    """Vista para ver el historial completo de una sesión de chat específica."""
    serializer_class = ChatSessionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


# --- VISTA DE INTEGRACIÓN PRINCIPAL ---

class SendMessageView(APIView):
    """
    El corazón de la integración. Recibe un mensaje de un usuario,
    lo procesa con el sistema RAG y devuelve la respuesta del bot.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_pk):
        try:
            # 1. Recupera la sesión de chat. Asegúrate de que pertenece al usuario.
            session = ChatSession.objects.get(pk=session_pk, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({"error": "Sesión de chat no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        user_message_text = request.data.get('message_text')
        if not user_message_text:
            return Response({"error": "El campo 'message_text' no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Guarda el mensaje del usuario en la base de datos
        ChatMessage.objects.create(
            session=session,
            sender='user',
            message_text=user_message_text
        )

        # 3. Llama al servicio RAG para obtener la respuesta del bot
        try:
            rag_service = rag_service()
            bot_response_text = rag_service.ask(user_message_text)
        except Exception as e:
            # Maneja posibles errores del servicio RAG (ej. API de Gemini caída)
            bot_response_text = "Lo siento, estoy teniendo problemas para procesar tu solicitud en este momento."
            print(f"Error en RAGService: {e}") # Log del error para debugging

        # 4. Guarda la respuesta del bot en la base de datos
        bot_message = ChatMessage.objects.create(
            session=session,
            sender='bot',
            message_text=bot_response_text
        )

        # 5. Devuelve solo la respuesta del bot al frontend
        serializer = ChatMessageSerializer(bot_message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
