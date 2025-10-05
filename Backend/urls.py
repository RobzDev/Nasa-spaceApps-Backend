from django.urls import path, include

urlpatterns = [
    path("api/", include("api.urls")),
    path('api/chat/', include('chat_api.urls')),

]
