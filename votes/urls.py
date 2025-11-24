from django.urls import path
from .views import VoteCreateView, PollResultsView, UserVoteView

urlpatterns = [
    path("", VoteCreateView.as_view(), name="vote-create"),
    path("results/<int:poll_id>/", PollResultsView.as_view(), name="poll-results"),
    path("me/<int:poll_id>/", UserVoteView.as_view(), name="user-vote"),  # NEW
]
