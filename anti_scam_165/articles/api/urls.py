from django.urls import path

from .views import ArticleCreateView
from .views import ArticleDetailView
from .views import ArticleListView
from .views import ArticleUpdateView

app_name = "articles"

urlpatterns = [
    path(
        "articles/",
        ArticleListView.as_view(),
        name="article-list",
    ),
    path(
        "articles/<int:id>/",
        ArticleDetailView.as_view(),
        name="article-detail",
    ),
    path(
        "articles/create/",
        ArticleCreateView.as_view(),
        name="article-create",
    ),
    path(
        "articles/<int:id>/update/",
        ArticleUpdateView.as_view(),
        name="article-update",
    ),
]
