import os
import google.generativeai as genai
from neomodel import db

# Configuración Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class RAGService:
    def __init__(self, generation_model="gemini-flash-lite-latest", embedding_model="text-embedding-004"):
        self.gen_model = genai.GenerativeModel(generation_model)
        self.embedding_model = embedding_model

    def embed_text(self, text: str):
        res = genai.embed_content(model=self.embedding_model, content=text)
        return res["embedding"]

    def semantic_search(self, query_text: str, limit: int = 1):
        embedding = self.embed_text(query_text)
        cypher = """
        CALL db.index.vector.queryNodes('chunk_embeddings', $limit, $embedding) 
        YIELD node AS chunk, score
        RETURN chunk.text AS text, score, chunk.uid AS uid
        """
        results, _ = db.cypher_query(cypher, {"limit": limit, "embedding": embedding})
        return [{"text": r[0], "score": r[1], "uid": r[2]} for r in results]

    def get_source_for_chunk(self, chunk_uid: str):
        cypher = """
        MATCH (c:Chunk {uid: $uid})<-[:HAS_CHUNK]-(a:Article)
        RETURN a.title AS title, a.link AS link, a.uid AS uid
        """
        rows, _ = db.cypher_query(cypher, {"uid": chunk_uid})
        if not rows:
            return None
        title, link, uid = rows[0]
        return {"title": title, "link": link, "uid": uid}

    def generate_answer(self, question: str, context_text: str, source: dict):
        prompt = f"""
Eres un asistente experto en biociencia espacial de la NASA.
Usa exclusivamente el siguiente contexto para responder:

CONTEXT:
---
{context_text}
---

QUESTION:
{question}

Responde de forma clara y concisa.  
Cita tu fuente así:
Fuente: {source['title']}. Enlace: {source['link']}
"""
        gen = self.gen_model.generate_content(prompt)
        return gen.text

    def ask(self, question: str):
        hits = self.semantic_search(question, limit=1)
        if not hits:
            return {"answer": None, "error": "no_relevant_context"}
        best = hits[0]
        source = self.get_source_for_chunk(best["uid"])
        if not source:
            return {"answer": None, "error": "no_source_found"}
        answer = self.generate_answer(question, best["text"], source)
        return {"answer": answer, "source": source}
