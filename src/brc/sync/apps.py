from django.apps import AppConfig


class SyncConfig(AppConfig):
    name = "brc.sync"

    def ready(self):
        from . import signals  # noqa
