from django.urls import path
from .views import (
    PollListCreateView,
    PollDetailView,
    OptionListCreateView,
    PollShareLinkView,
)

urlpatterns = [
    # List + Create polls
    path("", PollListCreateView.as_view(), name="poll-list-create"),

    # Shareable link (must be BEFORE pk route)
    path("share/<str:share_id>/", PollShareLinkView.as_view(), name="poll-share"),

    # Poll details
    path("<int:pk>/", PollDetailView.as_view(), name="poll-detail"),

    # Options for a poll
    path("<int:poll_id>/options/", OptionListCreateView.as_view(), name="poll-options"),
]
