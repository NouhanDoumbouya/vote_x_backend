from django.urls import path
from .views import (
    PollListCreateView,
    PollDetailView,
    OptionListCreateView,
)

urlpatterns = [
    path("", PollListCreateView.as_view(), name="poll-list-create"),
    path("<int:pk>/", PollDetailView.as_view(), name="poll-detail"),
    path("<int:poll_id>/options/", OptionListCreateView.as_view(), name="poll-options"),
]
