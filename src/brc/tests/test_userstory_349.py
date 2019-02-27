"""
Ref: https://github.com/VNG-Realisatie/gemma-zaken/issues/349
"""
from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.tests import JWTScopesMixin, get_operation_url

from brc.api.scopes import SCOPE_BESLUITEN_ALLES_VERWIJDEREN
from brc.datamodel.models import Besluit, BesluitInformatieObject
from brc.datamodel.tests.factories import BesluitFactory, BesluitInformatieObjectFactory


class US349TestCase(JWTScopesMixin, APITestCase):

    scopes = [SCOPE_BESLUITEN_ALLES_VERWIJDEREN]
    zaaktypes = ['*']

    def test_delete_besluit_cascades_properly(self):
        """
        Deleting a Besluit causes all related objects to be deleted as well.
        """
        besluit = BesluitFactory.create()

        BesluitInformatieObjectFactory.create(besluit=besluit)

        besluit_delete_url = get_operation_url('besluit_delete', uuid=besluit.uuid)

        response = self.client.delete(besluit_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        self.assertFalse(Besluit.objects.exists())

        self.assertFalse(BesluitInformatieObject.objects.exists())
