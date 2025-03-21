"""
Concrete view classes/utilities not tied to any particular app.
"""

import logging
import os
from collections import OrderedDict

from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from rest_framework import (
    authentication,
    exceptions as drf_exceptions,
    permissions,
    status,
)
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler as drf_exception_handler

from openforms.submissions.api.permissions import AnyActiveSubmissionPermission

from ..exception_handling import HandledException
from ..serializers import ExceptionSerializer

logger = logging.getLogger(__name__)


ERR_CONTENT_TYPE = "application/problem+json"


def exception_handler(exc, context):
    """
    Transform 4xx and 5xx errors into DSO-compliant shape.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        if os.getenv("DEBUG", "").lower() in ["yes", "1", "true"]:
            return None

        exc_message = args[0] if (args := exc.args) else type(exc).__name__
        logger.exception(exc_message, exc_info=True)

        # unkown type, so we use the generic Internal Server Error
        exc = drf_exceptions.APIException("Internal Server Error")
        response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    request = context.get("request")

    serializer = HandledException.as_serializer(exc, response, request)
    response.data = OrderedDict(serializer.data.items())
    # custom content type
    response["Content-Type"] = ERR_CONTENT_TYPE
    return response


class PingView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary=_("Ping the API"),
        description=_(
            "Pinging the API extends the user session. Note that you must be "
            "a staff user or have active submission(s) in your session."
        ),
        responses={
            200: str,
            "4XX": ExceptionSerializer,
        },
    )
    def get(self, request):
        return Response("pong van openforms", status=status.HTTP_200_OK)
