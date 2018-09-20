"""
Serializers of the Besluit Registratie Component REST API
"""
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from zds_schema.utils import lookup_kwargs_to_filters
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
    parent_retrieve_kwargs = {
        'besluit_uuid': 'uuid',
    }

    class Meta:
        model = BesluitInformatieObject
        fields = ('url', 'informatieobject')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'informatieobject': {'validators': [URLValidator()]},
        }

    def create(self, validated_data):
        view_kwargs = self.context['view'].kwargs
        filters = lookup_kwargs_to_filters(self.parent_retrieve_kwargs, view_kwargs)
        validated_data['besluit'] = get_object_or_404(Besluit, **filters)
        return super().create(validated_data)
