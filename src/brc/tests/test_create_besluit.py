from datetime import date, datetime

from django.test import override_settings
from django.utils import timezone

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.tests import TypeCheckMixin, get_operation_url

from brc.datamodel.constants import VervalRedenen
from brc.datamodel.models import Besluit
from brc.datamodel.tests.factories import (
    BesluitFactory, BesluitInformatieObjectFactory
)


@override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_200')
class BesluitCreateTests(TypeCheckMixin, APITestCase):

    @freeze_time('2018-09-06T12:08+0200')
    def test_us162_voeg_besluit_toe_aan_zaak(self):
        with self.subTest(part='besluit_create'):
            url = get_operation_url('besluit_create')

            # see https://github.com/VNG-Realisatie/gemma-zaken/issues/162#issuecomment-416598476
            response = self.client.post(url, {
                'verantwoordelijke_organisatie': '517439943',  # RSIN
                'besluittype': 'https://example.com/ztc/besluittype/abcd',
                'zaak': 'https://example.com/zrc/zaken/1234',
                'datum': '2018-09-06T11:00:00+0200',
                'toelichting': "Vergunning verleend.",
                'ingangsdatum': '2018-10-01',
                'vervaldatum': '2018-11-01',
                'vervalreden': VervalRedenen.tijdelijk,
            })

            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
            self.assertResponseTypes(response.data, (
                ('url', str),
                ('identificatie', str),
                ('verantwoordelijke_organisatie', str),
                ('besluittype', str),
                ('zaak', str),
                ('datum', str),
                ('toelichting', str),
                ('bestuursorgaan', str),
                ('ingangsdatum', str),
                ('vervaldatum', str),
                ('vervalreden', str),
                ('publicatiedatum', type(None)),
                ('verzenddatum', type(None)),
                ('uiterlijke_reactiedatum', type(None)),
            ))
            besluit_url = response.data['url']

            self.assertEqual(Besluit.objects.count(), 1)

            besluit = Besluit.objects.get()
            self.assertEqual(besluit.verantwoordelijke_organisatie, '517439943')
            self.assertEqual(besluit.besluittype, 'https://example.com/ztc/besluittype/abcd')
            self.assertEqual(besluit.zaak, 'https://example.com/zrc/zaken/1234')
            self.assertEqual(
                besluit.datum,
                datetime(2018, 9, 6, 9, 0, 0).replace(tzinfo=timezone.utc)
            )
            self.assertEqual(besluit.toelichting, "Vergunning verleend.")
            self.assertEqual(besluit.ingangsdatum, date(2018, 10, 1))
            self.assertEqual(besluit.vervaldatum, date(2018, 11, 1))
            self.assertEqual(besluit.vervalreden, VervalRedenen.tijdelijk)

        with self.subTest(part='besluitinformatieobject_create'):
            url = get_operation_url('besluitinformatieobject_create')

            response = self.client.post(url, {
                'besluit': besluit_url,
                'informatieobject': 'https://example.com/api/v1/enkelvoudigeinformatieobjecten/1234',
            })

            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
            self.assertResponseTypes(response.data, (
                ('url', str),
                ('besluit', str),
                ('informatieobject', str),
            ))

            self.assertEqual(besluit.besluitinformatieobject_set.count(), 1)
            self.assertEqual(
                besluit.besluitinformatieobject_set.get().informatieobject,
                'https://example.com/api/v1/enkelvoudigeinformatieobjecten/1234'
            )

    def test_opvragen_informatieobjecten_besluit(self):
        besluit1, besluit2 = BesluitFactory.create_batch(2)
        bio1_1, bio1_2, bio1_3 = BesluitInformatieObjectFactory.create_batch(3, besluit=besluit1)
        bio2_1, bio2_2 = BesluitInformatieObjectFactory.create_batch(2, besluit=besluit2)

        besluit1_url = get_operation_url('besluit_read', uuid=besluit1.uuid)
        besluit2_url = get_operation_url('besluit_read', uuid=besluit2.uuid)

        url = get_operation_url('besluitinformatieobject_list')

        response1 = self.client.get(url, {'besluit': besluit1_url})
        response2 = self.client.get(url, {'besluit': besluit2_url})

        self.assertEqual(len(response1.data), 3)
        self.assertEqual(
            {entry['besluit'] for entry in response1.data},
            {f"http://testserver{besluit1_url}"}
        )

        self.assertEqual(len(response2.data), 2)
        self.assertEqual(
            {entry['besluit'] for entry in response2.data},
            {f"http://testserver{besluit2_url}"}
        )
