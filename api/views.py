from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import ArticleSerializer, ChunkSerializer
from .services.rag_service import RAGService

class AskView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "Debes enviar 'question'"}, status=status.HTTP_400_BAD_REQUEST)

        rag = RAGService()
        result = rag.ask(question)

        if result.get("error"):
            return Response({"error": result["error"]}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "answer": result["answer"],
            "source": result["source"]
        }, status=status.HTTP_200_OK)
