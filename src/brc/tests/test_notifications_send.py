import json

from django.conf import settings
from django.test import override_settings

from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTScopesMixin, get_operation_url

from brc.datamodel.constants import VervalRedenen
from brc.datamodel.tests.factories import BesluitFactory, BesluitInformatieObjectFactory

@patch('zds_client.Client.request')
@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class SendNotifTestCase(JWTScopesMixin, APITestCase):

    def test_send_notif_create_besluit(self, mock_client):
        """
        Check if notifications will be send when Besluit is created
        """
        url = get_operation_url('besluit_create')
        data = {
            'verantwoordelijkeOrganisatie': '517439943',  # RSIN
            'besluittype': 'https://example.com/ztc/besluittype/abcd',
            'zaak': 'https://example.com/zrc/zaken/1234',
            'datum': '2018-09-06',
            'toelichting': "Vergunning verleend.",
            'ingangsdatum': '2018-10-01',
            'vervaldatum': '2018-11-01',
            'vervalreden': VervalRedenen.tijdelijk,
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        data = response.json()
        notif_args, notif_kwargs = mock_client.call_args_list[0]
        msg = json.loads(notif_kwargs['data'])

        self.assertEqual(notif_args[0], settings.NOTIFICATIES_URL)
        self.assertEqual(msg['kanaal'], settings.NOTIFICATIES_KANAAL)
        self.assertEqual(msg['resource'], 'besluit')
        self.assertEqual(msg['actie'], 'create')
        self.assertEqual(msg['resourceUrl'], data['url'])
        self.assertEqual(msg['kenmerken'][0]['verantwoordelijkeOrganisatie'], data['verantwoordelijkeOrganisatie'])
        self.assertEqual(msg['kenmerken'][1]['besluittype'], data['besluittype'])

    def test_send_notif_delete_resultaat(self, mock_client):
        """
        Check if notifications will be send when resultaat is deleted
        """
        besluit = BesluitFactory.create()
        bio = BesluitInformatieObjectFactory.create(besluit=besluit)
        bio_url = get_operation_url('besluiten_informatieobjecten_delete', uuid=bio.uuid, besluit_uuid=besluit.uuid)

        response = self.client.delete(bio_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        notif_args, notif_kwargs = mock_client.call_args_list[0]
        print(notif_args, notif_kwargs)
        msg = json.loads(notif_kwargs['data'])

        self.assertEqual(notif_args[0], settings.NOTIFICATIES_URL)
        self.assertEqual(msg['kanaal'], settings.NOTIFICATIES_KANAAL)
        self.assertEqual(msg['resource'], 'besluitinformatieobject')
        self.assertEqual(msg['actie'], 'destroy')
        self.assertEqual(msg['resourceUrl'], 'http://testserver{}'.format(bio_url))
        self.assertEqual(msg['kenmerken'][0]['verantwoordelijkeOrganisatie'], besluit.verantwoordelijke_organisatie)
        self.assertEqual(msg['kenmerken'][1]['besluittype'], besluit.besluittype)
