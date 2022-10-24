from django.apps import AppConfig

from vng_api_common.api import register_extensions


class BRCApiConfig(AppConfig):
    name = "brc.api"

    def ready(self):
        register_extensions()

        # ensure that the metaclass for every viewset has run
        from . import viewsets  # noqa
