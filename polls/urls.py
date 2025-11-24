from django.urls import path
from .views import (
    PollListCreateView,
    PollDetailView,
    OptionListCreateView,
    PollShareLinkView,
    AllowedUsersView,
    PollDeleteView,
)

urlpatterns = [
    path("", PollListCreateView.as_view(), name="poll-list-create"),
    path("<int:pk>/", PollDetailView.as_view(), name="poll-detail"),
    path("<int:poll_id>/options/", OptionListCreateView.as_view(), name="option-list-create"),
    path("share/<str:share_id>/", PollShareLinkView.as_view(), name="poll-share-link"),
    path("<int:poll_id>/allowed-users/", AllowedUsersView.as_view(), name="poll-allowed-users"),

    path("<int:pk>/delete/", PollDeleteView.as_view(), name="poll-delete"),
]
