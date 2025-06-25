from django.db import models
from django.utils.translation import gettext_lazy as _


class Article(models.Model):
    """
    Model to store anti-scam article data imported from CSV.
    Fields match the CSV structure: id, title, time, content.
    """

    # Use AutoField for explicit id management to match CSV IDs
    id = models.AutoField(primary_key=True, verbose_name=_("ID"))
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    time = models.DateTimeField(verbose_name=_("Publication Time"))
    content = models.TextField(verbose_name=_("Article Content"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        ordering = ["-time"]
        verbose_name = _("Anti-Scam Article")
        verbose_name_plural = _("Anti-Scam Articles")

    def __str__(self):
        return self.title
