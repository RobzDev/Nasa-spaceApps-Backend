from django.urls import path
from .views import AskView

urlpatterns = [
    path("rag/ask/", AskView.as_view(), name="rag-ask"),
]
