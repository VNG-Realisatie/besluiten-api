"""
Serializers of the Besluit Registratie Component REST API
"""
from django.utils.encoding import force_text

from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from vng_api_common.serializers import add_choice_values_help_text
from vng_api_common.validators import (
    InformatieObjectUniqueValidator, IsImmutableValidator,
    ObjectInformatieObjectValidator, UniekeIdentificatieValidator,
    URLValidator, validate_rsin
)

from brc.datamodel.constants import RelatieAarden, VervalRedenen
from brc.datamodel.models import Besluit, BesluitInformatieObject
from brc.sync.signals import SyncError

from .auth import get_drc_auth, get_zrc_auth, get_ztc_auth
from ..sync.signals import SyncError
from django.db import transaction


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

    @transaction.atomic()
    def save(self, **kwargs):
        try:
            return super().save(**kwargs)
        except SyncError as sync_error:
            # delete the object again
            raise serializers.ValidationError(
                {'zaak': sync_error.args[0]},
                code='sync-with-zrc'
            )


class BesluitInformatieObjectSerializer(serializers.HyperlinkedModelSerializer):
    aard_relatie_weergave = serializers.ChoiceField(
        source='get_aard_relatie_display', read_only=True,
        choices=[(force_text(value), key) for key, value in RelatieAarden.choices]
    )

    class Meta:
        model = BesluitInformatieObject
        fields = (
            'url',
            'informatieobject',
            'besluit',
            'aard_relatie_weergave',
        )
        extra_kwargs = {
            'url': {
                'lookup_field': 'uuid'
            },
            'informatieobject': {
                'validators': [
                    URLValidator(get_auth=get_drc_auth),
                    IsImmutableValidator(),
                ]
            },
            'besluit': {
                'lookup_field': 'uuid',
                'validators': [IsImmutableValidator()]
            }
        }

    def save(self, **kwargs):
        # can't slap a transaction atomic on this, since ZRC/BRC query for the
        # relation!
        try:
            return super().save(**kwargs)
        except SyncError as sync_error:
            # delete the object again
            BesluitInformatieObject.objects.filter(
                informatieobject=self.validated_data['informatieobject'],
                besluit=self.validated_data['besluit']
            )._raw_delete('default')
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: sync_error.args[0]
            }) from sync_error
