from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from anti_scam_165.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

app_name = "api"
urlpatterns = router.urls

# Include app API endpoints
urlpatterns += [
    path("", include("anti_scam_165.chat.api.urls", namespace="chat")),
    path("", include("anti_scam_165.articles.api.urls", namespace="articles")),
]
