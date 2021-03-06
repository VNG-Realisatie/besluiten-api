import uuid
from datetime import datetime
from unittest.mock import patch

from django.test import override_settings

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import (
    JWTAuthMixin,
    get_operation_url,
    get_validation_errors,
    reverse,
    reverse_lazy,
)
from zds_client.tests.mocks import mock_client

from brc.datamodel.models import Besluit, BesluitInformatieObject
from brc.datamodel.tests.factories import BesluitFactory, BesluitInformatieObjectFactory
from brc.sync.signals import SyncError

from .mixins import MockSyncMixin

INFORMATIEOBJECT = (
    f"http://drc.com/api/v1/enkelvoudiginformatieobjecten/{uuid.uuid4().hex}"
)
INFORMATIEOBJECTTYPE = "https://ztc.com/informatieobjecttypen/1234"
BESLUITTYPE = "https://ztc.com/besluittypen/1234"

RESPONSES = {
    BESLUITTYPE: {"url": BESLUITTYPE, "informatieobjecttypen": [INFORMATIEOBJECTTYPE]},
    INFORMATIEOBJECT: {
        "url": INFORMATIEOBJECT,
        "informatieobjecttype": INFORMATIEOBJECTTYPE,
    },
}


def dt_to_api(dt: datetime):
    formatted = dt.isoformat()
    if formatted.endswith("+00:00"):
        return formatted[:-6] + "Z"
    return formatted


@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200",
    ZDS_CLIENT_CLASS="vng_api_common.mocks.MockClient",
)
class BesluitInformatieObjectAPITests(MockSyncMixin, JWTAuthMixin, APITestCase):

    list_url = reverse_lazy("besluitinformatieobject-list", kwargs={"version": "1"})

    heeft_alle_autorisaties = True

    @freeze_time("2018-09-19T12:25:19+0200")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_create(self, *mocks):
        besluit = BesluitFactory.create(besluittype=BESLUITTYPE)
        besluit_url = reverse(besluit)
        content = {
            "informatieobject": INFORMATIEOBJECT,
            "besluit": "http://testserver" + besluit_url,
        }

        # Send to the API
        with mock_client(RESPONSES):
            response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # Test database
        self.assertEqual(BesluitInformatieObject.objects.count(), 1)
        stored_object = BesluitInformatieObject.objects.get()
        self.assertEqual(stored_object.besluit, besluit)

        expected_url = reverse(
            "besluitinformatieobject-detail",
            kwargs={"version": "1", "uuid": stored_object.uuid},
        )

        expected_response = content.copy()
        expected_response.update({"url": f"http://testserver{expected_url}"})
        self.assertEqual(response.json(), expected_response)

    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_duplicate_object(self, *mocks):
        """
        Test the (informatieobject, object) unique together validation.
        """
        bio = BesluitInformatieObjectFactory.create(
            informatieobject=INFORMATIEOBJECT, besluit__besluittype=BESLUITTYPE
        )
        besluit_url = reverse(bio.besluit)
        content = {
            "informatieobject": bio.informatieobject,
            "besluit": f"http://testserver{besluit_url}",
        }

        # Send to the API
        with mock_client(RESPONSES):
            response = self.client.post(self.list_url, content)

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )
        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "unique")

    def test_read_besluit(self):
        bio = BesluitInformatieObjectFactory.create(informatieobject=INFORMATIEOBJECT)
        # Retrieve from the API

        bio_detail_url = reverse(
            "besluitinformatieobject-detail", kwargs={"version": "1", "uuid": bio.uuid}
        )
        response = self.client.get(bio_detail_url)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        besluit_url = reverse(
            "besluit-detail", kwargs={"version": "1", "uuid": bio.besluit.uuid}
        )

        expected = {
            "url": f"http://testserver{bio_detail_url}",
            "informatieobject": bio.informatieobject,
            "besluit": f"http://testserver{besluit_url}",
        }

        self.assertEqual(response.json(), expected)

    def test_filter(self):
        bio = BesluitInformatieObjectFactory.create(informatieobject=INFORMATIEOBJECT)
        besluit_url = reverse(
            "besluit-detail", kwargs={"version": "1", "uuid": bio.besluit.uuid}
        )
        bio_list_url = reverse("besluitinformatieobject-list", kwargs={"version": "1"})

        response = self.client.get(
            bio_list_url,
            {"besluit": f"http://testserver.com{besluit_url}"},
            HTTP_HOST="testserver.com",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["besluit"], f"http://testserver.com{besluit_url}"
        )

    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_update_besluitinformatieobject_not_allowed(self, *mocks):
        besluit = BesluitFactory.create()
        besluit_url = reverse(
            "besluit-detail", kwargs={"version": "1", "uuid": besluit.uuid}
        )

        bio = BesluitInformatieObjectFactory.create(informatieobject=INFORMATIEOBJECT)
        bio_detail_url = reverse(
            "besluitinformatieobject-detail", kwargs={"version": "1", "uuid": bio.uuid}
        )

        response = self.client.patch(
            bio_detail_url,
            {
                "besluit": f"http://testserver{besluit_url}",
                "informatieobject": "https://bla.com",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_sync_create_fails(self):
        self.mocked_sync_create_bio.side_effect = SyncError("Sync failed")

        besluit = BesluitFactory.create()
        besluit_url = reverse(
            "besluit-detail", kwargs={"version": "1", "uuid": besluit.uuid}
        )

        content = {
            "informatieobject": INFORMATIEOBJECT,
            "besluit": f"http://testserver{besluit_url}",
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        # transaction must be rolled back
        self.assertFalse(BesluitInformatieObject.objects.exists())

    @freeze_time("2018-09-19T12:25:19+0200")
    def test_delete(self):
        bio = BesluitInformatieObjectFactory.create(informatieobject=INFORMATIEOBJECT)
        bio_url = reverse(
            "besluitinformatieobject-detail", kwargs={"version": "1", "uuid": bio.uuid}
        )

        self.assertEqual(self.mocked_sync_delete_bio.call_count, 0)

        response = self.client.delete(bio_url)
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

        self.assertEqual(self.mocked_sync_delete_bio.call_count, 1)

        # Relation is gone, besluit still exists.
        self.assertFalse(BesluitInformatieObject.objects.exists())
        self.assertTrue(Besluit.objects.exists())

    def test_validate_unknown_query_params(self):
        BesluitInformatieObjectFactory.create_batch(2)
        url = get_operation_url("besluitinformatieobject_list")

        response = self.client.get(url, {"someparam": "somevalue"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "unknown-parameters")
