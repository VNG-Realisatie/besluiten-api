"""
Serializers of the Besluit Registratie Component REST API
"""
from rest_framework import serializers
from zds_schema.validators import UniekeIdentificatieValidator, URLValidator

from brc.datamodel.models import Besluit, BesluitInformatieObject


class BesluitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Besluit
        fields = (
            'url',
            'identificatie',
            'verantwoordelijke_organisatie',
            'besluittype',
            'zaak',
            'datum',
            'toelichting',
            'bestuursorgaan',
            'ingangsdatum',
            'vervaldatum',
            'vervalreden',
            'publicatiedatum',
            'verzenddatum',
            'uiterlijke_reactiedatum',
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'zaak': {
                'validators': [URLValidator()],
            },
            'besluittype': {
                'validators': [URLValidator()],
            },
        }
        validators = [UniekeIdentificatieValidator('verantwoordelijke_organisatie')]


class BesluitInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BesluitInformatieObject
        fields = (
            'url',
            'besluit',
            'informatieobject',
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'besluit': {
                'lookup_field': 'uuid',
            },
            'informatieobject': {
                'validators': [URLValidator()],
            },
        }
