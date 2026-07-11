from django.urls import path

from . import views

urlpatterns = [
    path("conversations/", views.ConversationListCreateView.as_view(), name="conversation-list"),
    path(
        "conversations/<int:pk>/messages/",
        views.MessageListCreateView.as_view(),
        name="conversation-messages",
    ),
]
