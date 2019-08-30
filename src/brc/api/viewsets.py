from django.core.cache import caches

from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from vng_api_common.audittrails.viewsets import (
    AuditTrailCreateMixin, AuditTrailDestroyMixin, AuditTrailViewSet,
    AuditTrailViewsetMixin
)
from vng_api_common.notifications.viewsets import (
    NotificationCreateMixin, NotificationDestroyMixin,
    NotificationViewSetMixin
)
from vng_api_common.viewsets import CheckQueryParamsMixin

from brc.datamodel.models import Besluit, BesluitInformatieObject

from .audits import AUDIT_BRC
from .data_filtering import ListFilterByAuthorizationsMixin
from .filters import BesluitFilter, BesluitInformatieObjectFilter
from .kanalen import KANAAL_BESLUITEN
from .permissions import (
    BesluitAuthScopesRequired, BesluitRelatedAuthScopesRequired
)
from .scopes import (
    SCOPE_BESLUITEN_AANMAKEN, SCOPE_BESLUITEN_ALLES_LEZEN,
    SCOPE_BESLUITEN_ALLES_VERWIJDEREN, SCOPE_BESLUITEN_BIJWERKEN
)
from .serializers import BesluitInformatieObjectSerializer, BesluitSerializer


class BesluitViewSet(NotificationViewSetMixin,
                     AuditTrailViewsetMixin,
                     ListFilterByAuthorizationsMixin,
                     viewsets.ModelViewSet):
    """
    Opvragen en bewerken van BESLUITen.

    create:
    Maak een BESLUIT aan.

    Indien geen identificatie gegeven is, dan wordt deze automatisch
    gegenereerd.

    Er wordt gevalideerd op:
    - uniciteit van `verantwoorlijkeOrganisatie` + `identificatie`
    - geldigheid `verantwoorlijkeOrganisatie` RSIN
    - geldigheid `besluittype` URL
    - geldigheid `zaak` URL
    - `datum` in het verleden of nu

    list:
    Alle BESLUITen opvragen.

    Deze lijst kan gefilterd wordt met query-string parameters.

    retrieve:
    Een specifiek BESLUIT opvragen.

    Een specifiek BESLUIT opvragen.

    update:
    Werk een BESLUIT in zijn geheel bij.

    Er wordt gevalideerd op:
    - uniciteit van `verantwoorlijkeOrganisatie` + `identificatie`
    - geldigheid `verantwoorlijkeOrganisatie` RSIN
    - geldigheid `besluittype` URL
    - geldigheid `zaak` URL
    - `datum` in het verleden of nu

    partial_update:
    Werk een BESLUIT deels bij.

    Er wordt gevalideerd op:
    - uniciteit van `verantwoorlijkeOrganisatie` + `identificatie`
    - geldigheid `verantwoorlijkeOrganisatie` RSIN
    - geldigheid `besluittype` URL
    - geldigheid `zaak` URL
    - `datum` in het verleden of nu

    destroy:
    Verwijder een BESLUIT.

    Verwijder een BESLUIT samen met alle gerelateerde resources binnen deze API.

    **De gerelateerde resources zijn**
    - `BESLUITINFORMATIEOBJECT`
    - audit trail regels
    """
    queryset = Besluit.objects.all().order_by('-pk')
    serializer_class = BesluitSerializer
    filter_class = BesluitFilter
    lookup_field = 'uuid'
    pagination_class = PageNumberPagination
    permission_classes = (BesluitAuthScopesRequired, )
    required_scopes = {
        'list': SCOPE_BESLUITEN_ALLES_LEZEN,
        'retrieve': SCOPE_BESLUITEN_ALLES_LEZEN,
        'create': SCOPE_BESLUITEN_AANMAKEN,
        'destroy': SCOPE_BESLUITEN_ALLES_VERWIJDEREN,
        'update': SCOPE_BESLUITEN_BIJWERKEN,
        'partial_update': SCOPE_BESLUITEN_BIJWERKEN,
    }
    notifications_kanaal = KANAAL_BESLUITEN
    audit = AUDIT_BRC


class BesluitInformatieObjectViewSet(NotificationCreateMixin,
                                     NotificationDestroyMixin,
                                     AuditTrailCreateMixin,
                                     AuditTrailDestroyMixin,
                                     CheckQueryParamsMixin,
                                     ListFilterByAuthorizationsMixin,
                                     mixins.CreateModelMixin,
                                     mixins.DestroyModelMixin,
                                     viewsets.ReadOnlyModelViewSet):
    """
    Opvragen en bewerken van BESLUIT-INFORMATIEOBJECT relaties.

    create:
    Maak een BESLUIT-INFORMATIEOBJECT relatie aan.

    Registreer een INFORMATIEOBJECT bij een BESLUIT. Er worden twee types van
    relaties met andere objecten gerealiseerd:

    **Er wordt gevalideerd op**
    - geldigheid `besluit` URL
    - geldigheid `informatieobject` URL
    - de combinatie `informatieobject` en `besluit` moet uniek zijn

    **Opmerkingen**
    - De `registratiedatum` wordt door het systeem op 'NU' gezet. De
      `aardRelatie` wordt ook door het systeem gezet.
    - Bij het aanmaken wordt ook in de Documenten API de gespiegelde relatie
      aangemaakt, echter zonder de relatie-informatie.

    list:
    Alle BESLUIT-INFORMATIEOBJECT relaties opvragen.

    Deze lijst kan gefilterd wordt met query-string parameters.

    retrieve:
    Een specifieke BESLUIT-INFORMATIEOBJECT relatie opvragen.

    Een specifieke BESLUIT-INFORMATIEOBJECT relatie opvragen.

    update:
    Werk een BESLUIT-INFORMATIEOBJECT relatie in zijn geheel bij.

    Je mag enkel de gegevens van de relatie bewerken, en niet de relatie zelf
    aanpassen.

    **Er wordt gevalideerd op**
    - `informatieobject` URL en `besluit` URL mogen niet veranderen

    partial_update:
    Werk een BESLUIT-INFORMATIEOBJECT relatie deels bij.

    Je mag enkel de gegevens van de relatie bewerken, en niet de relatie zelf
    aanpassen.

    **Er wordt gevalideerd op**
    - `informatieobject` URL en `besluit` URL mogen niet veranderen

    destroy:
    Verwijder een BESLUIT-INFORMATIEOBJECT relatie.

    Verwijder een BESLUIT-INFORMATIEOBJECT relatie.
    """
    queryset = BesluitInformatieObject.objects.all()
    serializer_class = BesluitInformatieObjectSerializer
    filterset_class = BesluitInformatieObjectFilter
    lookup_field = 'uuid'
    permission_classes = (BesluitRelatedAuthScopesRequired,)
    required_scopes = {
        'list': SCOPE_BESLUITEN_ALLES_LEZEN,
        'retrieve': SCOPE_BESLUITEN_ALLES_LEZEN,
        'create': SCOPE_BESLUITEN_AANMAKEN,
        'destroy': SCOPE_BESLUITEN_ALLES_VERWIJDEREN,
        'update': SCOPE_BESLUITEN_BIJWERKEN,
        'partial_update': SCOPE_BESLUITEN_BIJWERKEN,
    }
    notifications_kanaal = KANAAL_BESLUITEN
    notifications_main_resource_key = 'besluit'
    audit = AUDIT_BRC

    def get_queryset(self):
        qs = super().get_queryset()

        # Do not display BesluitInformatieObjecten that are marked to be deleted
        cache = caches['drc_sync']
        marked_bios = cache.get('bios_marked_for_delete')
        if marked_bios:
            return qs.exclude(uuid__in=marked_bios)
        return qs


class BesluitAuditTrailViewSet(AuditTrailViewSet):
    """
    Opvragen van de audit trail regels.

    list:
    Alle audit trail regels behorend bij het BESLUIT.

    Alle audit trail regels behorend bij het BESLUIT.

    retrieve:
    Een specifieke audit trail regel opvragen.

    Een specifieke audit trail regel opvragen.
    """
    main_resource_lookup_field = 'besluit_uuid'
