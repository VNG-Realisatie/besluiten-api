from django.apps import AppConfig


class BRCApiConfig(AppConfig):
    name = 'brc.api'

    def ready(self):
        # ensure that the metaclass for every viewset has run
        from . import viewsets  # noqa
