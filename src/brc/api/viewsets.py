from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.reverse import reverse
from vng_api_common.notifications.kanalen import Kanaal
from vng_api_common.notifications.viewsets import NotificationViewSetMixin
from vng_api_common.permissions import permission_class_factory
from vng_api_common.utils import lookup_kwargs_to_filters
from vng_api_common.viewsets import NestedViewSetMixin

from brc.datamodel.models import Besluit, BesluitInformatieObject

from .filters import BesluitFilter
from .kanalen import KANAAL_BESLUITEN
from .permissions import BesluitAuthScopesRequired, BesluitBaseAuthRequired
from .scopes import (
    SCOPE_BESLUITEN_ALLES_LEZEN, SCOPE_BESLUITEN_ALLES_VERWIJDEREN,
    SCOPE_BESLUITEN_BIJWERKEN
)
from .serializers import BesluitInformatieObjectSerializer, BesluitSerializer


class BesluitViewSet(NotificationViewSetMixin, viewsets.ModelViewSet):
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
        'create': SCOPE_BESLUITEN_BIJWERKEN,
        'destroy': SCOPE_BESLUITEN_ALLES_VERWIJDEREN,
        'update': SCOPE_BESLUITEN_BIJWERKEN,
        'partial_update': SCOPE_BESLUITEN_BIJWERKEN,
    }
    notifications_kanaal = KANAAL_BESLUITEN


class BesluitInformatieObjectViewSet(NotificationViewSetMixin,
                                     NestedViewSetMixin,
                                     viewsets.ModelViewSet):
    """
    Opvragen en bwerken van Besluit-Informatieobject relaties.

    create:
    Registreer in welk(e) INFORMATIEOBJECT(en) een BESLUIT vastgelegd is.

    Er wordt gevalideerd op:
    - geldigheid informatieobject URL
    - uniek zijn van relatie BESLUIT-INFORMATIEOBJECT
    - bestaan van relatie BESLUIT-INFORMATIEOBJECT in het DRC waar het
      informatieobject leeft

    list:
    Geef een lijst van relaties tussen BESLUITen en INFORMATIEOBJECTen.

    update:
    Werk de relatie tussen een BESLUIT en INFORMATIEOBJECT bij.

    Er wordt gevalideerd op:
    - geldigheid informatieobject URL
    - uniek zijn van relatie BESLUIT-INFORMATIEOBJECT
    - bestaan van relatie BESLUIT-INFORMATIEOBJECT in het DRC waar het
      informatieobject leeft

    partial_update:
    Werk de relatie tussen een BESLUIT en INFORMATIEOBJECT bij.

    Er wordt gevalideerd op:
    - geldigheid informatieobject URL
    - uniek zijn van relatie BESLUIT-INFORMATIEOBJECT
    - bestaan van relatie BESLUIT-INFORMATIEOBJECT in het DRC waar het
      informatieobject leeft

    destroy:
    Ontkoppel een BESLUIT en INFORMATIEOBJECT-relatie.
    """
    queryset = BesluitInformatieObject.objects.all()
    serializer_class = BesluitInformatieObjectSerializer
    lookup_field = 'uuid'
    parent_retrieve_kwargs = {
        'besluit_uuid': 'uuid',
    }
    permission_classes = (
        permission_class_factory(
            base=BesluitBaseAuthRequired,
            get_obj='_get_besluit',
        ),
    )
    required_scopes = {
        'list': SCOPE_BESLUITEN_ALLES_LEZEN,
        'retrieve': SCOPE_BESLUITEN_ALLES_LEZEN,
        'create': SCOPE_BESLUITEN_BIJWERKEN,
        'destroy': SCOPE_BESLUITEN_ALLES_VERWIJDEREN,
        'update': SCOPE_BESLUITEN_BIJWERKEN,
        'partial_update': SCOPE_BESLUITEN_BIJWERKEN,
    }
    notifications_kanaal = KANAAL_BESLUITEN

    def _get_besluit(self):
        if not hasattr(self, '_besluit'):
            filters = lookup_kwargs_to_filters(self.parent_retrieve_kwargs, self.kwargs)
            self._besluit = get_object_or_404(Besluit, **filters)
        return self._besluit

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # DRF introspection
        if not self.kwargs:
            return context
        context['parent_object'] = self._get_besluit()
        return context

    def get_notification_main_object_url(self, data: dict, kanaal: Kanaal) -> str:
        besluit = self._get_besluit()
        return reverse('besluit-detail', kwargs={'uuid': besluit.uuid}, request=self.request)
