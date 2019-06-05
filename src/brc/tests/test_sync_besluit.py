from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_operation_url

from brc.api.tests.mixins import BesluitSyncMixin
from brc.datamodel.constants import VervalRedenen
from brc.datamodel.models import Besluit
from brc.datamodel.tests.factories import BesluitFactory
from brc.sync.signals import SyncError


@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200'
)
class BesluitSyncCreateTests(BesluitSyncMixin, JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    def test_create_sync_besluit(self):
        url = get_operation_url('besluit_create')

        response = self.client.post(url, {
            'verantwoordelijke_organisatie': '517439943',
            'besluittype': 'https://example.com/ztc/besluittype/abcd',
            'zaak': 'https://example.com/zrc/zaken/1234',
            'datum': '2018-09-06',
            'toelichting': "Vergunning verleend.",
            'ingangsdatum': '2018-10-01',
            'vervaldatum': '2018-11-01',
            'vervalreden': VervalRedenen.tijdelijk,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.mocked_sync_create_besluit.assert_called_once()
        self.mocked_sync_delete_besluit.assert_not_called()

        besluit = Besluit.objects.get()

        self.mocked_sync_create_besluit.assert_called_with(besluit)

    def test_delete_sync_besluit(self):
        besluit = BesluitFactory.create()
        url = get_operation_url('besluit_read', uuid=besluit.uuid)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        args = self.mocked_sync_delete_besluit.call_args[0]

        #  can't assert args directly because besluit object doesn't longer exist
        self.assertEqual(args[0].uuid, besluit.uuid)

    def test_create_sync_fails(self):
        self.mocked_sync_create_besluit.side_effect = SyncError("Sync failed")

        url = get_operation_url('besluit_create')

        response = self.client.post(url, {
            'verantwoordelijke_organisatie': '517439943',
            'besluittype': 'https://example.com/ztc/besluittype/abcd',
            'zaak': 'https://example.com/zrc/zaken/1234',
            'datum': '2018-09-06',
            'toelichting': "Vergunning verleend.",
            'ingangsdatum': '2018-10-01',
            'vervaldatum': '2018-11-01',
            'vervalreden': VervalRedenen.tijdelijk,
        })

        # Test response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        # transaction must be rolled back
        self.assertFalse(Besluit.objects.exists())
