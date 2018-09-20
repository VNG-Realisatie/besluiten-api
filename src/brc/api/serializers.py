"""
Serializers of the Besluit Registratie Component REST API
"""
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from zds_schema.validators import (
    InformatieObjectUniqueValidator, ObjectInformatieObjectValidator,
    UniekeIdentificatieValidator, URLValidator
)

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
                'validators': [URLValidator(headers={'Accept-Crs': 'EPSG:4326'})],
            },
            'besluittype': {
                'validators': [URLValidator()],
            },
        }
        validators = [UniekeIdentificatieValidator('verantwoordelijke_organisatie')]


class BesluitInformatieObjectSerializer(NestedHyperlinkedModelSerializer):
    parent_lookup_kwargs = {
        'besluit_uuid': 'besluit__uuid'
    }

    class Meta:
        model = BesluitInformatieObject
        fields = ('url', 'informatieobject')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'informatieobject': {
                'validators': [
                    URLValidator(),
                    InformatieObjectUniqueValidator('besluit', 'informatieobject'),
                    ObjectInformatieObjectValidator(),
                ]
            },
        }

    def create(self, validated_data):
        besluit = self.context['parent_object']
        validated_data['besluit'] = besluit
        return super().create(validated_data)
