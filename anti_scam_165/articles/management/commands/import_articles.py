import csv
import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from anti_scam_165.articles.models import Article


class ValidationError(CommandError):
    """Error for CSV validation issues"""


class CSVReadError(CommandError):
    """Error for CSV reading issues"""


class InvalidRowError(Exception):
    """Error for invalid row data"""


class Command(BaseCommand):
    help = "Import anti-scam articles from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-file",
            type=str,
            default="anti_scam_article.csv",
            help="Path to the CSV file (default: anti_scam_article.csv in "
            "project root)",
        )

    def _validate_csv_columns(self, reader: csv.DictReader) -> None:
        """Validate that CSV has required columns."""
        expected_columns = ["id", "title", "time", "content"]
        if not all(col in reader.fieldnames for col in expected_columns):
            missing_cols = ", ".join(expected_columns)
            found_cols = ", ".join(reader.fieldnames)
            error_msg = (
                f"CSV file must contain columns: {missing_cols}. Found: {found_cols}"
            )
            raise ValidationError(error_msg)

    def _parse_datetime(self, time_str: str) -> datetime.datetime:
        """Parse datetime string with timezone awareness."""
        try:
            # Try standard ISO format
            return datetime.datetime.fromisoformat(time_str)
        except ValueError:
            # we manually add UTC timezone to make it aware
            format_with_no_tz = "%Y/%m/%d %H:%M"
            return datetime.datetime.strptime(
                time_str,
                format_with_no_tz,
            ).replace(tzinfo=datetime.UTC)

    def _process_row(self, row: dict) -> tuple[Article, bool, bool]:
        """Process a single row from the CSV."""
        try:
            article_id = int(row["id"])
            title = row["title"]
            time = self._parse_datetime(row["time"])
            content = row["content"]

            # Check if article already exists and update/create as needed
            article, created = Article.objects.update_or_create(
                id=article_id,
                defaults={"title": title, "time": time, "content": content},
            )

            # Determine if anything actually changed for existing records
            is_updated = (
                False
                if created
                else not (
                    article.title == title
                    and article.time == time
                    and article.content == content
                )
            )
        except ValueError as e:
            # More specific exception for data conversion issues
            error_message = f"Invalid data format: {e}"
            raise InvalidRowError(error_message) from e
        else:
            return article, created, is_updated

    def _resolve_csv_path(self, csv_file: str) -> Path:
        """Resolve the CSV file path."""
        csv_path = Path(csv_file)

        # If just filename is provided, look in project root
        if not csv_path.is_absolute():
            csv_path = (
                Path(settings.BASE_DIR)
                / "anti_scam_165"
                / "articles"
                / "data"
                / csv_file
            )

        if not csv_path.exists():
            error_msg = f"CSV file not found: {csv_path}"
            raise CommandError(error_msg)

        return csv_path

    def _import_articles(self, csv_path: Path) -> dict[str, int]:
        """Import articles from CSV file."""
        stats = {"created": 0, "updated": 0, "unchanged": 0, "error": 0}

        try:
            with csv_path.open(encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self._validate_csv_columns(reader)

                for row in reader:
                    try:
                        article, created, is_updated = self._process_row(row)

                        if created:
                            stats["created"] += 1
                            self.stdout.write(
                                f"Created article: {article.title} (ID: {article.id})",
                            )
                        elif is_updated:
                            stats["updated"] += 1
                            self.stdout.write(
                                f"Updated article: {article.title} (ID: {article.id})",
                            )
                        else:
                            stats["unchanged"] += 1

                    except InvalidRowError as e:
                        stats["error"] += 1
                        self.stderr.write(
                            self.style.ERROR(
                                f"Invalid row {row.get('id', 'unknown')}: {e}",
                            ),
                        )

        except csv.Error as e:
            error_msg = f"Error reading CSV file: {e}"
            raise CSVReadError(error_msg) from e

        return stats

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        csv_path = self._resolve_csv_path(csv_file)

        self.stdout.write(f"Importing articles from: {csv_path}")

        try:
            stats = self._import_articles(csv_path)

            # Print summary
            self.stdout.write(
                self.style.SUCCESS(
                    f"Import completed: {stats['created']} created, "
                    f"{stats['updated']} updated, {stats['unchanged']} unchanged, "
                    f"{stats['error']} errors",
                ),
            )
        except (ValidationError, CSVReadError):
            # These are already properly formatted with good messages
            raise
        except Exception as e:
            # Last resort catch-all with proper chaining
            error_msg = f"Unexpected error during import: {e}"
            raise CommandError(error_msg) from e
