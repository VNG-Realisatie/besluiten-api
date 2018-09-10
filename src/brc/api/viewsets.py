from rest_framework import mixins, viewsets

from brc.datamodel.models import Besluit, BesluitInformatieObject

from .filters import BesluitFilter, BesluitInformatieObjectFilter
from .serializers import BesluitInformatieObjectSerializer, BesluitSerializer


class BesluitViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
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
    """
    queryset = Besluit.objects.all()
    serializer_class = BesluitSerializer
    filter_class = BesluitFilter
    lookup_field = 'uuid'


class BesluitInformatieObjectViewSet(viewsets.ModelViewSet):
    """
    Opvragen en bwerken van Besluit-Informatieobject relaties.

    create:
    Registreer in welk(e) INFORMATIEOBJECT(en) een BESLUIT vastgelegd is.

    Er wordt gevalideerd op:
    - geldigheid besluit URL
    - geldigheid informatieobject URL

    list:
    Geef een lijst van relaties tussen BESLUITen en INFORMATIEOBJECTen.

    Door te filteren op besluit en/of informatieobject kan je opvragen in welke
    informatieobjecten een besluit is vastgelegd, of welke besluiten in een
    informatieobject vastgelegd zijn.

    update:
    Werk de relatie tussen een ZAAK en INFORMATIEOBJECT bij.

    Er wordt gevalideerd op:
    - geldigheid besluit URL
    - geldigheid informatieobject URL

    partial_update:
    Werk de relatie tussen een ZAAK en INFORMATIEOBJECT bij.

    Er wordt gevalideerd op:
    - geldigheid besluit URL
    - geldigheid informatieobject URL

    destroy:
    Ontkoppel een ZAAK en INFORMATIEOBJECT-relatie.
    """
    queryset = BesluitInformatieObject.objects.all()
    serializer_class = BesluitInformatieObjectSerializer
    filter_class = BesluitInformatieObjectFilter
    lookup_field = 'uuid'
