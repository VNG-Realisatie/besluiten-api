"""
Guarantee that the proper authorization amchinery is in place.
"""
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import (
    AuthCheckMixin, JWTAuthMixin, get_operation_url, reverse
)

from brc.datamodel.tests.factories import (
    BesluitFactory, BesluitInformatieObjectFactory
)

from ..scopes import SCOPE_BESLUITEN_ALLES_LEZEN, SCOPE_BESLUITEN_BIJWERKEN


@override_settings(ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient')
class BesluitScopeForbiddenTests(AuthCheckMixin, APITestCase):

    def test_cannot_create_besluit_without_correct_scope(self):
        url = reverse('besluit-list')
        self.assertForbidden(url, method='post')

    def test_cannot_read_without_correct_scope(self):
        besluit = BesluitFactory.create()
        bio = BesluitInformatieObjectFactory.create(besluit=besluit)
        urls = [
            reverse('besluit-list'),
            reverse(besluit),
            reverse('besluitinformatieobject-list', kwargs={'besluit_uuid': besluit.uuid}),
            reverse(bio, kwargs={'besluit_uuid': besluit.uuid})
        ]

        for url in urls:
            with self.subTest(url=url):
                self.assertForbidden(url, method='get')


class BesluitReadCorrectScopeTests(JWTAuthMixin, APITestCase):
    scopes = [SCOPE_BESLUITEN_ALLES_LEZEN]
    besluittype = 'https://besluittype.nl/ok'

    def test_besluit_list(self):
        """
        Assert you can only list BESLUITen of the besluittypes of your authorization
        """
        BesluitFactory.create(besluittype='https://besluittype.nl/ok')
        BesluitFactory.create(besluittype='https://besluittype.nl/not_ok')
        url = reverse('besluit-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['besluittype'], 'https://besluittype.nl/ok')

    def test_besluit_retreive(self):
        """
        Assert you can only read BESLUITen of the besluittypes of your authorization
        """
        besluit1 = BesluitFactory.create(besluittype='https://besluittype.nl/ok')
        besluit2 = BesluitFactory.create(besluittype='https://besluittype.nl/not_ok')
        url1 = reverse(besluit1)
        url2 = reverse(besluit2)

        response1 = self.client.get(url1)
        response2 = self.client.get(url2)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_superuser(self):
        """
        superuser read everything
        """
        self.applicatie.heeft_alle_autorisaties = True
        self.applicatie.save()

        BesluitFactory.create(besluittype='https://besluittype.nl/ok')
        BesluitFactory.create(besluittype='https://besluittype.nl/not_ok')
        url = reverse('besluit-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(len(response_data), 2)

@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='vng_api_common.mocks.ObjectInformatieObjectClient'
)
class BioReadTests(JWTAuthMixin, APITestCase):

    scopes = [SCOPE_BESLUITEN_ALLES_LEZEN, SCOPE_BESLUITEN_BIJWERKEN]
    besluittype = 'https://besluittype.nl/ok'

    def test_list_bio_limited_to_authorized_zaken(self):
        besluit1 = BesluitFactory.create(besluittype='https://besluittype.nl/ok')
        besluit2 = BesluitFactory.create(besluittype='https://besluittype.nl/not_ok')
        url1 = reverse('besluitinformatieobject-list', kwargs={'besluit_uuid': besluit1.uuid})
        url2 = reverse('besluitinformatieobject-list', kwargs={'besluit_uuid': besluit2.uuid})

        # must show up
        BesluitInformatieObjectFactory.create(besluit=besluit1)
        # must not show up
        BesluitInformatieObjectFactory.create(besluit=besluit2)

        response1 = self.client.get(url1)
        response2 = self.client.get(url2)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        response_data1 = response1.json()
        response_data2 = response2.json()

        self.assertEqual(len(response_data1), 1)
        self.assertEqual(len(response_data2), 0)

    def test_create_bio_limited_to_authorized_zaken(self):
        besluit1 = BesluitFactory.create(besluittype='https://besluittype.nl/ok')
        besluit2 = BesluitFactory.create(besluittype='https://besluittype.nl/not_ok')
        url1 = reverse('besluitinformatieobject-list', kwargs={'besluit_uuid': besluit1.uuid})
        url2 = reverse('besluitinformatieobject-list', kwargs={'besluit_uuid': besluit2.uuid})
        data = {'informatieobject': 'https://example.com/api/v1/enkelvoudigeinformatieobjecten/1234'}

        response1 = self.client.post(url1, data)
        response2 = self.client.post(url2, data)

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED, response1.data)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN, response2.data)

    def test_detail_zaakinformatieobject_limited_to_authorized_zaken(self):
        besluit1 = BesluitFactory.create(besluittype='https://besluittype.nl/ok')
        besluit2 = BesluitFactory.create(besluittype='https://besluittype.nl/not_ok')
        # must show up
        bio1 = BesluitInformatieObjectFactory.create(besluit=besluit1)
        # must not show up
        bio2 = BesluitInformatieObjectFactory.create(besluit=besluit2)

        url1 = reverse(bio1, kwargs={'besluit_uuid': besluit1.uuid})
        url2 = reverse(bio2, kwargs={'besluit_uuid': besluit2.uuid})

        response1 = self.client.get(url1)
        response2 = self.client.get(url2)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
