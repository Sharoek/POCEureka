from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler as drf_exception_handler
from rest_framework import (
    authentication,
    exceptions as drf_exceptions,
    permissions,
    status,
)
from drf_spectacular.utils import extend_schema

class PingView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary=("Ping the API"),
        description=(
            "Pinging the API extends the user session. Note that you must be "
            "a staff user or have active submission(s) in your session."
        ),
        responses={
            200: str,
        },
    )
    def get(self, request):
        return Response("pong van openzaak", status=status.HTTP_200_OK)