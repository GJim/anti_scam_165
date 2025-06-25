import secrets
import string

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Conversation

User = get_user_model()


def generate_random_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for i in range(length))


# Constants for tests
TEST_PASSWORD = generate_random_password()  # nosec B105
NUM_TOTAL_CONVERSATIONS = 2  # Total number of test conversations


class ConversationAPITests(APITestCase):
    def setUp(self):
        # Create a regular test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            # Using test password for testing purposes only
            password=TEST_PASSWORD,  # nosec B106
        )

        # Create another regular user for testing permissions
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            # Using test password for testing purposes only
            password=TEST_PASSWORD,  # nosec B106
        )

        # Create an admin user for testing admin access
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            # Using test password for testing purposes only
            password=TEST_PASSWORD,  # nosec B106
        )
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()

        # Authenticate as the test user
        self.client.force_authenticate(user=self.user)

        # Create test conversations for the users
        self.user_conversation = Conversation.objects.create(
            user=self.user,
            question="What is the meaning of life?",
            content="Test conversation content",
            status="completed",
        )

        self.other_conversation = Conversation.objects.create(
            user=self.other_user,
            question="How does quantum computing work?",
            content="Other user's conversation",
            status="completed",
        )

    def test_create_conversation(self):
        """Test creating a new conversation"""
        url = reverse("api:chat:conversation-create")
        data = {"question": "Is artificial intelligence conscious?"}
        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data

        # Verify the conversation was created in the database
        conversation_id = response.data["id"]
        conversation = Conversation.objects.get(id=conversation_id)
        assert conversation.user == self.user  # Check user association
        # Check question was saved
        assert conversation.question == "Is artificial intelligence conscious?"

    def test_get_conversation(self):
        """Test retrieving a conversation"""
        url = reverse(
            "api:chat:conversation-detail",
            kwargs={"id": self.user_conversation.id},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == self.user_conversation.id
        # Check question is returned
        assert response.data["question"] == "What is the meaning of life?"
        assert response.data["content"] == "Test conversation content"
        assert response.data["status"] == "completed"

    def test_cannot_retrieve_other_user_conversation(self):
        """Test that a user cannot retrieve another user's conversation"""
        url = reverse(
            "api:chat:conversation-detail",
            kwargs={"id": self.other_conversation.id},
        )
        response = self.client.get(url)

        # Should return 404 Not Found instead of 403 Forbidden to not leak information
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_conversations(self):
        """Test listing a user's conversations"""
        url = reverse("api:chat:conversation-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should only see their own conversation
        assert len(response.data) == 1
        assert response.data[0]["id"] == self.user_conversation.id

    def test_admin_can_list_all_conversations(self):
        """Test that admin users can list all conversations"""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("api:chat:conversation-list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should see all conversations
        assert len(response.data) == NUM_TOTAL_CONVERSATIONS

        # Check that both conversations are in the response
        conversation_ids = [item["id"] for item in response.data]
        assert self.user_conversation.id in conversation_ids
        assert self.other_conversation.id in conversation_ids

    def test_admin_can_access_any_conversation(self):
        """Test that admin users can access any conversation"""
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)

        # Try to access other user's conversation
        url = reverse(
            "api:chat:conversation-detail",
            kwargs={"id": self.other_conversation.id},
        )
        response = self.client.get(url)

        # Should be able to access it
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == self.other_conversation.id
        assert response.data["content"] == "Other user's conversation"
