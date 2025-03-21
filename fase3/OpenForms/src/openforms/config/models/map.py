from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class MapTileLayerManager(models.Manager["MapTileLayer"]):
    def get_by_natural_key(self, identifier: str) -> MapTileLayer:
        return self.get(identifier=identifier)


class MapTileLayer(models.Model):
    identifier = models.SlugField(
        _("identifier"),
        unique=True,
        max_length=50,
        help_text=_("A unique identifier for the tile layer."),
    )
    url = models.URLField(
        _("tile layer url"),
        max_length=255,
        help_text=_(
            "URL to the tile layer image, used to define the map component "
            "background. To ensure correct functionality of the map, "
            "EPSG 28992 projection should be used. "
            "Example value: https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/standaard/EPSG:28992/{z}/{x}/{y}.png"
        ),
    )
    label = models.CharField(
        _("label"),
        max_length=100,
        help_text=_(
            "An easily recognizable name for the tile layer, used to identify it."
        ),
    )

    objects = MapTileLayerManager()

    class Meta:
        verbose_name = _("map tile layer")
        verbose_name_plural = _("map tile layers")
        ordering = ("label",)

    def __str__(self):
        return self.label

    def natural_key(self):
        return (self.identifier,)
