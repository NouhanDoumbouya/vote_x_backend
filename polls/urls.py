# polls/urls.py
from django.urls import path
from .views import (
    PollListView,
    PollCreateView,
    PollDetailView,
    PollResultsView,
    PollVoteView,
    PollShareLinkView,
)

urlpatterns = [
    # List polls (public/private/restricted filtering)
    path("", PollListView.as_view(), name="poll-list"),

    # Create poll (authenticated)
    path("create/", PollCreateView.as_view(), name="poll-create"),

    # Shareable link access
    path("share/<str:share_id>/", PollShareLinkView.as_view(), name="poll-share"),

    # Poll details
    path("<int:pk>/", PollDetailView.as_view(), name="poll-detail"),

    # Poll results
    path("<int:pk>/results/", PollResultsView.as_view(), name="poll-results"),

    # Voting endpoint
    path("<int:pk>/vote/", PollVoteView.as_view(), name="poll-vote"),
]
