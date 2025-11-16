from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Let DRF handle standard exceptions first
    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            "success": False,
            "message": response.data.get("detail") or "An error occurred.",
            "errors": response.data if isinstance(response.data, dict) else None
        }, status=response.status_code)

    # Handle unexpected errors (500)
    return Response({
        "success": False,
        "message": "An unexpected error occurred. Please try again later.",
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
