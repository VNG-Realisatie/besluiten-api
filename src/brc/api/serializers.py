"""
Serializers of the Besluit Registratie Component REST API
"""
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from vng_api_common.serializers import add_choice_values_help_text
from vng_api_common.validators import (
    InformatieObjectUniqueValidator, IsImmutableValidator,
    ObjectInformatieObjectValidator, UniekeIdentificatieValidator,
    URLValidator, validate_rsin
)

from brc.datamodel.constants import VervalRedenen
from brc.datamodel.models import Besluit, BesluitInformatieObject

from .auth import get_drc_auth, get_zrc_auth, get_ztc_auth


class BesluitSerializer(serializers.HyperlinkedModelSerializer):
    vervalreden_weergave = serializers.CharField(source='get_vervalreden_display', read_only=True)

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
            'vervalreden_weergave',
            'publicatiedatum',
            'verzenddatum',
            'uiterlijke_reactiedatum',
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid',
            },
            'identificatie': {
                'validators': [IsImmutableValidator()],
            },
            'verantwoordelijke_organisatie': {
                'validators': [IsImmutableValidator(), validate_rsin],
            },
            'zaak': {
                'validators': [URLValidator(get_auth=get_zrc_auth, headers={'Accept-Crs': 'EPSG:4326'})],
            },
            'besluittype': {
                'validators': [URLValidator(get_auth=get_ztc_auth)],
            },
        }
        validators = [UniekeIdentificatieValidator('verantwoordelijke_organisatie')]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        value_display_mapping = add_choice_values_help_text(VervalRedenen)
        self.fields['vervalreden'].help_text += f"\n\n{value_display_mapping}"


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
                    URLValidator(get_auth=get_drc_auth),
                    InformatieObjectUniqueValidator('besluit', 'informatieobject'),
                    ObjectInformatieObjectValidator(),
                ]
            },
        }

    def create(self, validated_data):
        besluit = self.context['parent_object']
        validated_data['besluit'] = besluit
        return super().create(validated_data)
