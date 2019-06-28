from django.core.cache import cache

from rest_framework import viewsets
from vng_api_common.audittrails.viewsets import (
    AuditTrailViewSet, AuditTrailViewsetMixin
)
from vng_api_common.notifications.viewsets import NotificationViewSetMixin
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
    Opvragen en bewerken van BESLUITen

    create:
    Registreer een besluit.

    Indien geen identificatie gegeven is, dan wordt deze automatisch
    gegenereerd.

    Er wordt gevalideerd op:
    - uniciteit van verantwoorlijke organisatie + identificatie
    - RSIN verantwoorlijke organisatie
    - geldigheid besluittype URL
    - geldigheid zaak URL
    - datum in het verleden of nu

    list:
    Geef een lijst van BESLUITen, waarin gefiltered kan worden.

    retrieve:
    Geef de details van 1 enkel BESLUIT.

    update:
    Werk een BESLUIT bij.

    Er wordt gevalideerd op:
    - uniciteit van verantwoorlijke organisatie + identificatie
    - RSIN verantwoorlijke organisatie
    - geldigheid besluittype URL
    - geldigheid zaak URL
    - datum in het verleden of nu

    partial_update:
    Werk een BESLUIT bij.

    Er wordt gevalideerd op:
    - uniciteit van verantwoorlijke organisatie + identificatie
    - RSIN verantwoorlijke organisatie
    - geldigheid besluittype URL
    - geldigheid zaak URL
    - datum in het verleden of nu

    destroy:
    Verwijdert een BESLUIT, samen met alle gerelateerde resources binnen deze API.

    **De gerelateerde resources zijn**
    - `BesluitInformatieObject` - de relaties van het Besluit naar de
      informatieobjecten
    """
    queryset = Besluit.objects.all()
    serializer_class = BesluitSerializer
    filter_class = BesluitFilter
    lookup_field = 'uuid'
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


class BesluitInformatieObjectViewSet(NotificationViewSetMixin,
                                     AuditTrailViewsetMixin,
                                     CheckQueryParamsMixin,
                                     ListFilterByAuthorizationsMixin,
                                     viewsets.ModelViewSet):
    """
    Opvragen en bewerken van Besluit-Informatieobject relaties.

    create:
    Registreer een INFORMATIEOBJECT bij een BESLUIT. Er worden twee types van
    relaties met andere objecten gerealiseerd:

    **Er wordt gevalideerd op**
    - geldigheid besluit URL
    - geldigheid informatieobject URL
    - de combinatie informatieobject en besluit moet uniek zijn

    **Opmerkingen**
    - De registratiedatum wordt door het systeem op 'NU' gezet. De `aardRelatie`
      wordt ook door het systeem gezet.
    - Bij het aanmaken wordt ook in het DRC de gespiegelde relatie aangemaakt,
      echter zonder de relatie-informatie.


    Registreer welk(e) INFORMATIEOBJECT(en) een BESLUIT kent.

    **Er wordt gevalideerd op**
    - geldigheid informatieobject URL
    - uniek zijn van relatie BESLUIT-INFORMATIEOBJECT

    list:
    Geef een lijst van relaties tussen INFORMATIEOBJECTen en BESLUITen.

    Deze lijst kan gefilterd wordt met querystringparameters.

    retrieve:
    Geef de details van een relatie tussen een INFORMATIEOBJECT en een BESLUIT.

    update:
    Update een INFORMATIEOBJECT bij een BESLUIT. Je mag enkel de gegevens
    van de relatie bewerken, en niet de relatie zelf aanpassen.

    **Er wordt gevalideerd op**
    - informatieobject URL en besluit URL mogen niet veranderen

    partial_update:
    Update een INFORMATIEOBJECT bij een BESLUIT. Je mag enkel de gegevens
    van de relatie bewerken, en niet de relatie zelf aanpassen.

    **Er wordt gevalideerd op**
    - informatieobject URL en besluit URL mogen niet veranderen

    destroy:
    Verwijdert de relatie tussen BESLUIT en INFORMATIEOBJECT.
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
        marked_bios = cache.get('bios_marked_for_delete')
        if marked_bios:
            return qs.exclude(uuid__in=marked_bios)
        return qs


class BesluitAuditTrailViewSet(AuditTrailViewSet):
    main_resource_lookup_field = 'besluit_uuid'
