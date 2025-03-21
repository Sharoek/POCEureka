from django.db import models
from django.utils.translation import gettext_lazy as _

from solo.models import SingletonModel


class MSGraphRegistrationConfigManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("service")


class MSGraphRegistrationConfig(SingletonModel):
    """
    global configuration and defaults
    """

    service = models.OneToOneField(
        "microsoft.MSGraphService",
        verbose_name=_("Microsoft Graph service"),
        on_delete=models.PROTECT,
        related_name="registration_config",
        blank=True,
        null=True,
    )

    objects = MSGraphRegistrationConfigManager()

    class Meta:
        verbose_name = _("Microsoft Graph registration")
