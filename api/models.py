from neomodel import (
    StructuredNode, StringProperty, DateTimeProperty, 
    RelationshipTo, RelationshipFrom, UniqueIdProperty, 
    ArrayProperty, FloatProperty, JSONProperty
)
import datetime

class Article(StructuredNode):
    """
    Representa un artículo/documento en la base.
    """
    uid = UniqueIdProperty()
    title = StringProperty(required=True, index=True)
    link = StringProperty(required=False)
    metadata = JSONProperty(required=False)
    published_at = DateTimeProperty(default=datetime.datetime.utcnow)

    # relación con chunks
    has_chunk = RelationshipTo("Chunk", "HAS_CHUNK")


class Chunk(StructuredNode):
    """
    Fragmento de texto con embedding.
    """
    uid = UniqueIdProperty()
    text = StringProperty(required=True)
    embedding = ArrayProperty(FloatProperty(), required=False)  # vector
    metadata = JSONProperty(required=False)
    created_at = DateTimeProperty(default=datetime.datetime.utcnow)

    # relación inversa al artículo
    article = RelationshipFrom(Article, "HAS_CHUNK")
