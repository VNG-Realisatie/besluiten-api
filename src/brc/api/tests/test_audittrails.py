import unittest
from copy import deepcopy

from django.test import override_settings

from rest_framework.test import APITestCase
from vng_api_common.audittrails.models import AuditTrail
from vng_api_common.tests import JWTAuthMixin, reverse
from zds_client.tests.mocks import mock_client

from brc.datamodel.models import Besluit, BesluitInformatieObject

# ZTC
ZTC_ROOT = 'https://example.com/ztc/api/v1'
DRC_ROOT = 'https://example.com/drc/api/v1'
CATALOGUS = f'{ZTC_ROOT}/catalogus/878a3318-5950-4642-8715-189745f91b04'
BESLUITTYPE = f'{CATALOGUS}/besluittypen/283ffaf5-8470-457b-8064-90e5728f413f'
INFORMATIE_OBJECT = f'{DRC_ROOT}/enkelvoudiginformatieobjecten/1234'


@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient'
)
class AuditTrailTests(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    responses = {
        BESLUITTYPE: {
            'url': BESLUITTYPE,
            'productenOfDiensten': [
                'https://example.com/product/123',
                'https://example.com/dienst/123',
            ]
        }
    }

    def _create_besluit(self):
        url = reverse(Besluit)

        besluit_data = {
            'verantwoordelijkeOrganisatie': '000000000',
            'besluittype': BESLUITTYPE,
            'datum': '2019-04-25',
            'ingangsdatum': '2019-04-26',
            'vervaldatum': '2019-04-28'
        }
        with mock_client(self.responses):
            response = self.client.post(url, besluit_data)

        return response.data

    def test_create_besluit_audittrail(self):
        besluit_response = self._create_besluit()

        audittrails = AuditTrail.objects.filter(hoofd_object=besluit_response['url'])
        self.assertEqual(audittrails.count(), 1)

        # Verify that the audittrail for the Besluit creation contains the correct
        # information
        besluit_create_audittrail = audittrails.get()
        self.assertEqual(besluit_create_audittrail.bron, 'BRC')
        self.assertEqual(besluit_create_audittrail.actie, 'create')
        self.assertEqual(besluit_create_audittrail.resultaat, 201)
        self.assertEqual(besluit_create_audittrail.oud, None)
        self.assertEqual(besluit_create_audittrail.nieuw, besluit_response)

    def test_update_besluit_audittrails(self):
        besluit_data = self._create_besluit()

        modified_data = deepcopy(besluit_data)
        url = modified_data.pop('url')
        modified_data['toelichting'] = 'aangepast'

        with mock_client(self.responses):
            response = self.client.put(url, modified_data)
            besluit_response = response.data

        audittrails = AuditTrail.objects.filter(hoofd_object=besluit_response['url'])
        self.assertEqual(audittrails.count(), 2)

        # Verify that the audittrail for the Besluit update contains the correct
        # information
        besluit_update_audittrail = audittrails[1]
        self.assertEqual(besluit_update_audittrail.bron, 'BRC')
        self.assertEqual(besluit_update_audittrail.actie, 'update')
        self.assertEqual(besluit_update_audittrail.resultaat, 200)
        self.assertEqual(besluit_update_audittrail.oud, besluit_data)
        self.assertEqual(besluit_update_audittrail.nieuw, besluit_response)

    def test_partial_update_besluit_audittrails(self):
        besluit_data = self._create_besluit()

        with mock_client(self.responses):
            response = self.client.patch(besluit_data['url'], {
                'toelichting': 'aangepast'
            })
            besluit_response = response.data

        audittrails = AuditTrail.objects.filter(hoofd_object=besluit_response['url'])
        self.assertEqual(audittrails.count(), 2)

        # Verify that the audittrail for the Besluit partial_update contains the
        # correct information
        besluit_update_audittrail = audittrails[1]
        self.assertEqual(besluit_update_audittrail.bron, 'BRC')
        self.assertEqual(besluit_update_audittrail.actie, 'partial_update')
        self.assertEqual(besluit_update_audittrail.resultaat, 200)
        self.assertEqual(besluit_update_audittrail.oud, besluit_data)
        self.assertEqual(besluit_update_audittrail.nieuw, besluit_response)

    def test_create_besluitinformatieobject_audittrail(self):
        besluit_data = self._create_besluit()

        besluit_uuid = besluit_data['url'].split('/')[-1]
        url = reverse(BesluitInformatieObject, kwargs={'besluit_uuid': besluit_uuid})

        response = self.client.post(url, {
            'informatieobject': INFORMATIE_OBJECT,
        })

        besluitinformatieobject_response = response.data

        audittrails = AuditTrail.objects.filter(hoofd_object=besluit_data['url'])
        self.assertEqual(audittrails.count(), 2)

        # Verify that the audittrail for the BesluitInformatieObject creation
        # contains the correct information
        bio_create_audittrail = audittrails[1]
        self.assertEqual(bio_create_audittrail.bron, 'BRC')
        self.assertEqual(bio_create_audittrail.actie, 'create')
        self.assertEqual(bio_create_audittrail.resultaat, 201)
        self.assertEqual(bio_create_audittrail.oud, None)
        self.assertEqual(bio_create_audittrail.nieuw, besluitinformatieobject_response)

    def test_delete_besluit_cascade_audittrails(self):
        besluit_data = self._create_besluit()

        # Delete the Besluit
        response = self.client.delete(besluit_data['url'])

        # Verify that deleting the Besluit deletes all related AuditTrails
        audittrails = AuditTrail.objects.filter(hoofd_object=besluit_data['url'])
        self.assertFalse(audittrails.exists())

    def test_audittrail_applicatie_information(self):
        besluit_response = self._create_besluit()

        audittrail = AuditTrail.objects.filter(hoofd_object=besluit_response['url']).get()

        # Verify that the application id stored in the AuditTrail matches
        # the id of the Application used for the request
        self.assertEqual(audittrail.applicatie_id, str(self.applicatie.uuid))

        # Verify that the application representation stored in the AuditTrail
        # matches the label of the Application used for the request
        self.assertEqual(audittrail.applicatie_weergave, self.applicatie.label)
