from django.contrib import admin
from django.urls import path, include

# Swagger imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="VoteX API",
        default_version="v1",
        description="API documentation for the Online Poll System Backend",
        contact=openapi.Contact(email="nouhandoumbouya655@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    # Admin site
    path("admin/", admin.site.urls),

    # Authentication and user management
    path("api/auth/", include("users.urls")),

    # Polls management
    path("api/polls/", include("polls.urls")),

    # Voting management
    path("api/votes/", include("votes.urls")),

    # Swagger
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc-ui"),
    path("api/schema.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]
