from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("A conflict occurred")
    default_code = "conflict"


class Gone(APIException):
    status_code = status.HTTP_410_GONE
    default_detail = _("The resource is gone")
    default_code = "gone"


class PreconditionFailed(APIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = _("Precondition failed")
    default_code = "precondition_failed"


class RequestEntityTooLarge(APIException):
    status_code = 413  # does not exist in rest_framework.status
    default_detail = _("Request entity too large")
    default_code = "request_entity_too_large"


class UnprocessableEntity(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _("Request understood and validated, but cannot be processed.")
    default_code = "unprocessable_entity"


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _("Service is not available.")
    default_code = "service_unavailable"
