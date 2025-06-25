from rest_framework import serializers

from anti_scam_165.chat.models import Conversation


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new Conversation object with a user question."""

    class Meta:
        model = Conversation
        fields = ["id", "question"]
        read_only_fields = ["id"]


class ConversationResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a Conversation response.
    """

    class Meta:
        model = Conversation
        fields = [
            "id",
            "question",
            "status",
            "error",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "error",
            "content",
            "created_at",
            "updated_at",
        ]
