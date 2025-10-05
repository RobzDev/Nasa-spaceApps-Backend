from django.urls import path
from .views import (
    UserCreateView,
    ChatSessionListView,
    ChatSessionDetailView,
    SendMessageView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Rutas de Autenticación y Registro
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Rutas para gestionar sesiones de chat
    path('sessions/', ChatSessionListView.as_view(), name='session-list-create'),
    path('sessions/<int:pk>/', ChatSessionDetailView.as_view(), name='session-detail'),

    # Ruta principal para enviar un mensaje y obtener respuesta del bot
    path('sessions/<int:session_pk>/send_message/', SendMessageView.as_view(), name='send-message'),
]