import google.generativeai as genai
from django.conf import settings # Para leer la clave desde settings.py
from neomodel import db

class RAGService:
    def __init__(self):
        """
        El constructor de la clase. Se ejecuta cada vez que se crea una instancia.
        Aquí es el lugar perfecto para configurar la API Key.
        """
        # --- CORRECCIÓN ---
        # Leemos la clave desde settings.py y la pasamos usando el argumento 'api_key'.
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        except AttributeError:
            # Esto es un seguro en caso de que olvides poner la clave en settings.py
            raise Exception("La variable GEMINI_API_KEY no está configurada en settings.py")

        self.generation_model = genai.GenerativeModel('gemini-pro')
        self.embedding_model = 'models/text-embedding-004'

    def _embed_text(self, text: str) -> list[float]:
        """Convierte texto en un vector."""
        result = genai.embed_content(model=self.embedding_model, content=text)
        return result['embedding']

    def _semantic_search(self, query_text: str, limit: int = 1) -> dict | None:
        """Realiza la búsqueda vectorial en Neo4j."""
        query_embedding = self._embed_text(query_text)
        
        cypher = """
        CALL db.index.vector.queryNodes('chunk_embeddings', $limit, $embedding) 
        YIELD node AS chunk, score
        RETURN chunk.text AS text, score
        """
        
        # Usamos el driver de neomodel para ejecutar la consulta de forma segura
        results, _ = db.cypher_query(cypher, {'limit': limit, 'embedding': query_embedding})
        
        if not results:
            return None
            
        return {'text': results[0][0], 'score': results[0][1]}

    def _get_source_for_chunk(self, chunk_text: str) -> dict | None:
        """Encuentra el artículo de origen para un chunk de texto dado."""
        cypher = """
        MATCH (c:Chunk {text: $chunk_text})<-[:HAS_CHUNK]-(a:Article)
        RETURN a.title AS title, a.link AS link
        """
        results, _ = db.cypher_query(cypher, {'chunk_text': chunk_text})

        if not results:
            return None

        return {'title': results[0][0], 'link': results[0][1]}

    def _generate_response(self, question: str, context: str, source: dict) -> str:
        """Genera la respuesta final con Gemini."""
        # (El prompt sigue siendo el mismo)
        prompt = f"""
        Eres un asistente experto. Tu tarea es responder a la pregunta del usuario basándote únicamente en el siguiente contexto.

        Contexto:
        ---
        {context}
        ---
        Pregunta: "{question}"

        Instrucciones:
        1. Responde de forma clara y concisa.
        2. Basa tu respuesta solo en el contexto. No añadas conocimiento externo.
        3. Al final, cita tu fuente así: "Fuente: {source['title']} ({source['link']})"
        """
        response = self.generation_model.generate_content(prompt)
        return response.text

    def ask(self, question: str) -> str:
        """Orquesta el proceso completo de RAG."""
        search_result = self._semantic_search(question)
        
        if not search_result:
            return "Lo siento, no pude encontrar información relevante para responder a tu pregunta."

        context_chunk = search_result['text']
        source = self._get_source_for_chunk(context_chunk)
        
        if not source:
            return "Encontré información relevante, pero no pude rastrear el artículo de origen."

        return self._generate_response(question, context_chunk, source)