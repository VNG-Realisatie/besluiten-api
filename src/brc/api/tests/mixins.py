from unittest.mock import patch

from notifications_api_common.models import NotificationsConfig
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service


class BesluitInformatieObjectSyncMixin:
    def setUp(self):
        super().setUp()

        patcher_sync_create = patch("brc.sync.signals.sync_create_bio")
        self.mocked_sync_create_bio = patcher_sync_create.start()
        self.addCleanup(patcher_sync_create.stop)

        patcher_sync_delete = patch("brc.sync.signals.sync_delete_bio")
        self.mocked_sync_delete_bio = patcher_sync_delete.start()
        self.addCleanup(patcher_sync_delete.stop)


class BesluitSyncMixin:
    def setUp(self):
        super().setUp()

        patcher_sync_create = patch("brc.sync.signals.sync_create_besluit")
        self.mocked_sync_create_besluit = patcher_sync_create.start()
        self.addCleanup(patcher_sync_create.stop)

        patcher_sync_delete = patch("brc.sync.signals.sync_delete_besluit")
        self.mocked_sync_delete_besluit = patcher_sync_delete.start()
        self.addCleanup(patcher_sync_delete.stop)


class MockSyncMixin(BesluitSyncMixin, BesluitInformatieObjectSyncMixin):
    pass


class NotificationsConfigMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls._configure_notifications()

    @staticmethod
    def _configure_notifications(api_root=None):
        svc, _ = Service.objects.update_or_create(
            api_root=api_root or "https://notificaties-api.vng.cloud/api/v1/",
            defaults=dict(
                label="Notifications API",
                api_type=APITypes.nrc,
                client_id="some-client-id",
                secret="some-secret",
                auth_type=AuthTypes.zgw,
            ),
        )
        config = NotificationsConfig.get_solo()
        config.notifications_api_service = svc
        config.save()
