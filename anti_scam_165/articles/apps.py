from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# Import signals conditionally to avoid issues during initial setup
# We use a try/except block at the module level to prevent import errors
# during Django's initialization when the database might not be ready yet
ARTICLES_SIGNALS = None
try:
    import anti_scam_165.articles.signals

    ARTICLES_SIGNALS = anti_scam_165.articles.signals
except ImportError:
    pass


class ArticlesConfig(AppConfig):
    name = "anti_scam_165.articles"
    verbose_name = _("Articles")

    def ready(self):
        # Signal handling is done by importing the signals module
        # at the top level with error suppression
        pass
