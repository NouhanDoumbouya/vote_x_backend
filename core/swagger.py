from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="VoteX API Documentation",
        default_version='v1',
        description="Interactive API documentation for the VoteX backend.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@votex.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
