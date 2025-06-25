import csv
import datetime
import io
import secrets
import string
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from anti_scam_165.articles.models import Article

User = get_user_model()


def generate_random_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for i in range(length))


# Constants for tests
TEST_PASSWORD = generate_random_password()  # nosec B105
NUM_TOTAL_ARTICLES = 2  # Total number of test articles


class ArticleModelTests(TestCase):
    """Tests for the Article model."""

    def setUp(self):
        self.article_data = {
            "title": "Test Article",
            "time": datetime.datetime(2025, 6, 25, 12, 0, tzinfo=datetime.UTC),
            "content": "This is a test article content.",
        }
        self.article = Article.objects.create(**self.article_data)

    def test_article_creation(self):
        """Test that article is created correctly"""
        assert self.article.title == self.article_data["title"]
        assert self.article.time == self.article_data["time"]
        assert self.article.content == self.article_data["content"]

    def test_article_str_representation(self):
        """Test the string representation of an article"""
        assert str(self.article) == self.article_data["title"]


class ArticleAPITests(APITestCase):
    """Tests for the Article API endpoints."""

    def setUp(self):
        # Create a regular user and admin user
        self.user = User.objects.create_user(
            username="testuser",
            email="user@example.com",
            password=TEST_PASSWORD,  # nosec B106
        )

        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password=TEST_PASSWORD,  # nosec B106
        )

        # Create test articles
        self.article1 = Article.objects.create(
            title="Test Article 1",
            time=datetime.datetime(2025, 6, 25, 12, 0, tzinfo=datetime.UTC),
            content="Content of test article 1",
        )

        self.article2 = Article.objects.create(
            title="Test Article 2",
            time=datetime.datetime(2025, 6, 25, 14, 0, tzinfo=datetime.UTC),
            content="Content of test article 2",
        )

        self.article_data = {
            "title": "New Test Article",
            "time": "2025-06-25T15:00:00Z",
            "content": "Content of new test article",
        }

        self.client = APIClient()

    def test_article_list_authenticated(self):
        """Test that authenticated users can list articles"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("api:articles:article-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == NUM_TOTAL_ARTICLES

    def test_article_list_unauthenticated(self):
        """Test that unauthenticated users cannot list articles"""
        self.client.logout()
        response = self.client.get(reverse("api:articles:article-list"))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_article_detail_authenticated(self):
        """Test that authenticated users can view article details"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("api:articles:article-detail", kwargs={"id": self.article1.id}),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == self.article1.title

    def test_article_create_admin(self):
        """Test that admin users can create articles"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse("api:articles:article-create"),
            self.article_data,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Article.objects.count() == NUM_TOTAL_ARTICLES + 1  # Three articles now
        assert Article.objects.filter(title=self.article_data["title"]).exists()

    def test_article_create_non_admin(self):
        """Test that non-admin users cannot create articles"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("api:articles:article-create"),
            self.article_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Article.objects.count() == NUM_TOTAL_ARTICLES  # Still only two articles

    def test_article_update_admin(self):
        """Test that admin users can update articles"""
        self.client.force_authenticate(user=self.admin_user)
        update_data = {
            "title": "Updated Article Title",
            "time": "2025-06-25T16:00:00Z",
            "content": "Updated content",
        }
        response = self.client.put(
            reverse("api:articles:article-update", kwargs={"id": self.article1.id}),
            update_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        self.article1.refresh_from_db()
        assert self.article1.title == update_data["title"]

    def test_article_update_non_admin(self):
        """Test that non-admin users cannot update articles"""
        self.client.force_authenticate(user=self.user)
        update_data = {
            "title": "Attempted Update",
            "time": "2025-06-25T16:00:00Z",
            "content": "Attempted update content",
        }
        response = self.client.put(
            reverse("api:articles:article-update", kwargs={"id": self.article1.id}),
            update_data,
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.article1.refresh_from_db()
        assert self.article1.title != update_data["title"]


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImportArticlesCommandTests(TestCase):
    """Tests for the import_articles management command."""

    def setUp(self):
        # Create a temporary directory
        self.temp_dir = Path(settings.MEDIA_ROOT)

        # Create a test CSV file
        self.csv_path = self.temp_dir / "test_articles.csv"
        with self.csv_path.open("w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["id", "title", "time", "content"])
            writer.writerow(
                [
                    "1",
                    "CSV Test Article 1",
                    "2025-06-20 10:00:00",
                    "Content from CSV file 1",
                ],
            )
            writer.writerow(
                [
                    "2",
                    "CSV Test Article 2",
                    "2025-06-21 11:00:00",
                    "Content from CSV file 2",
                ],
            )

    def test_import_command(self):
        """Test the import_articles command."""
        # Call the command
        out = io.StringIO()
        call_command("import_articles", f"--csv-file={self.csv_path}", stdout=out)
        output = out.getvalue()

        # Check that articles were created
        assert "created" in output.lower()
        assert Article.objects.count() == NUM_TOTAL_ARTICLES

        # Verify the imported data
        article1 = Article.objects.get(id=1)
        assert article1.title == "CSV Test Article 1"

        # Run the command again to test idempotency
        out = io.StringIO()
        call_command("import_articles", f"--csv-file={self.csv_path}", stdout=out)
        output = out.getvalue()

        # Check for unchanged counts in output
        assert "unchanged" in output.lower()

        # Verify no duplicates were created
        assert Article.objects.count() == NUM_TOTAL_ARTICLES

    def test_import_with_update(self):
        """Test the import updates existing articles without duplicating."""
        # First import
        call_command("import_articles", f"--csv-file={self.csv_path}")

        # Modify the CSV file with updated content
        with self.csv_path.open("w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["id", "title", "time", "content"])
            writer.writerow(
                ["1", "Updated CSV Article", "2025-06-20 10:00:00", "Updated content"],
            )
            writer.writerow(
                [
                    "2",
                    "CSV Test Article 2",
                    "2025-06-21 11:00:00",
                    "Content from CSV file 2",
                ],
            )

        # Re-import
        out = io.StringIO()
        call_command("import_articles", f"--csv-file={self.csv_path}", stdout=out)
        output = out.getvalue()

        # Check that articles were updated
        assert "updated" in output.lower()
        assert Article.objects.count() == NUM_TOTAL_ARTICLES  # Still only two articles

        # Verify the updated data
        article1 = Article.objects.get(id=1)
        assert article1.title == "Updated CSV Article"
        assert article1.content == "Updated content"
