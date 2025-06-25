from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated

from anti_scam_165.articles.models import Article

from .serializers import ArticleCreateSerializer
from .serializers import ArticleSerializer
from .serializers import ArticleUpdateSerializer


class ArticleListView(ListAPIView):
    """
    API view for listing all articles.
    """

    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticated]


class ArticleDetailView(RetrieveAPIView):
    """
    API view for retrieving article details.
    """

    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "id"


class ArticleCreateView(CreateAPIView):
    """
    API view for creating a new article.
    Only admin users can create articles.
    """

    serializer_class = ArticleCreateSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()


class ArticleUpdateView(RetrieveUpdateAPIView):
    """
    API view for updating an existing article.
    Only admin users can update articles.
    """

    serializer_class = ArticleUpdateSerializer
    queryset = Article.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = "id"
