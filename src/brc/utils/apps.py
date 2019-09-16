from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "brc.utils"

    def ready(self):
        from . import checks  # noqa
