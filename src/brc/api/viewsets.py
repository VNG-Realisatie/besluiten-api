from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from vng_api_common.utils import lookup_kwargs_to_filters
from vng_api_common.viewsets import NestedViewSetMixin

from .scopes import SCOPE_BESLUITEN_ALLES_VERWIJDEREN
from brc.datamodel.models import Besluit, BesluitInformatieObject

from .filters import BesluitFilter
from .serializers import BesluitInformatieObjectSerializer, BesluitSerializer


class BesluitViewSet(viewsets.ModelViewSet):
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
    required_scopes = {
        'destroy': SCOPE_BESLUITEN_ALLES_VERWIJDEREN,
    }


class BesluitInformatieObjectViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # DRF introspection
        if not self.kwargs:
            return context
        filters = lookup_kwargs_to_filters(self.parent_retrieve_kwargs, self.kwargs)
        context['parent_object'] = get_object_or_404(Besluit, **filters)
        return context
