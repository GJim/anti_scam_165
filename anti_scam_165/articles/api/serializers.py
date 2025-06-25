from rest_framework import serializers

from anti_scam_165.articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    Main serializer for the Article model - used for listing and retrieving articles.
    """

    class Meta:
        model = Article
        fields = ["id", "title", "time", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ArticleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Article objects.
    """

    class Meta:
        model = Article
        fields = ["id", "title", "time", "content"]
        read_only_fields = ["id"]


class ArticleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing Article objects.
    """

    class Meta:
        model = Article
        fields = ["id", "title", "time", "content"]
        read_only_fields = ["id"]
