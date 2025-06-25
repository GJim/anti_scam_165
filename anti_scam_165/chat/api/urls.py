from django.urls import path

from .views import ConversationCreateView
from .views import ConversationListView
from .views import ConversationRetrieveView

app_name = "chat"

urlpatterns = [
    path(
        "conversations/",
        ConversationCreateView.as_view(),
        name="conversation-create",
    ),
    path(
        "conversations/list/",
        ConversationListView.as_view(),
        name="conversation-list",
    ),
    path(
        "conversations/<int:id>/",
        ConversationRetrieveView.as_view(),
        name="conversation-detail",
    ),
]
