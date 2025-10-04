from rest_framework import serializers

class ChunkSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    text = serializers.CharField()
    embedding = serializers.ListField(
        child=serializers.FloatField(),
        required=False
    )
    metadata = serializers.JSONField(required=False)
    created_at = serializers.DateTimeField(read_only=True)


class ArticleSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    title = serializers.CharField()
    link = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)
    published_at = serializers.DateTimeField(required=False)

    # nested chunks
    chunks = ChunkSerializer(many=True, required=False)
