import factory

from ..models import TimelineLogProxy


class TimelineLogProxyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TimelineLogProxy
