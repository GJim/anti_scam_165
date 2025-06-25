from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from anti_scam_165.chat.models import Conversation
from anti_scam_165.chat.tasks import process_conversation

from .serializers import ConversationCreateSerializer
from .serializers import ConversationResponseSerializer


class ConversationCreateView(CreateAPIView):
    """
    API view for creating a new conversation.
    This will trigger a long running task and return the conversation ID.
    Conversation is associated with the logged-in user.
    """

    serializer_class = ConversationCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Get the question from the validated data
        question = serializer.validated_data.get("question")

        # Create a new conversation record associated with the current user
        conversation = Conversation.objects.create(
            user=self.request.user,
            question=question,
        )

        # Start the long-running task asynchronously
        task = process_conversation.delay(conversation.id)

        # Update the conversation with the task ID
        conversation.task_id = task.id
        conversation.save()

        # Set the conversation instance for the serializer
        serializer.instance = conversation


class ConversationListView(ListAPIView):
    """
    API view for listing conversations.
    Regular users can only see their own conversations.
    Admin users can see all conversations.
    """

    serializer_class = ConversationResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # If user is admin or staff, return all conversations
        if user.is_staff or user.is_superuser:
            return Conversation.objects.all()
        # Otherwise, only return conversations owned by the current user
        return Conversation.objects.filter(user=user)


class ConversationRetrieveView(RetrieveAPIView):
    """
    API view for retrieving conversation status and result.
    Regular users can only access their own conversations.
    Admin users can access any conversation.
    """

    serializer_class = ConversationResponseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        # If user is admin or staff, allow access to any conversation
        if user.is_staff or user.is_superuser:
            return Conversation.objects.all()
        # Otherwise, only allow access to conversations owned by the current user
        return Conversation.objects.filter(user=user)
