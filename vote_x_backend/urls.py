from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin site
    path("admin/", admin.site.urls),

    # Authentication and user management
    path("api/auth/", include("users.urls")),

    # Polls management
    path("api/polls/", include("polls.urls")),

    # Voting management
    path("api/votes/", include("votes.urls")),
]
