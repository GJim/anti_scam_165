from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from anti_scam_165.articles.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin configuration for Article model."""

    list_display = ["id", "title", "time", "created_at", "updated_at"]
    list_display_links = ["id", "title"]
    search_fields = ["title", "content"]
    list_filter = ["time", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["title", "time", "content"]}),
        (_("Metadata"), {"fields": ["created_at", "updated_at"]}),
    ]
    ordering = ["-time"]
