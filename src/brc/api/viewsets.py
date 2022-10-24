from django.core.cache import caches
from django.utils.translation import gettext as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from notifications_api_common.viewsets import (
    NotificationCreateMixin,
    NotificationDestroyMixin,
    NotificationViewSetMixin,
)
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from vng_api_common.audittrails.viewsets import (
    AuditTrailCreateMixin,
    AuditTrailDestroyMixin,
    AuditTrailViewSet,
    AuditTrailViewsetMixin,
)
from vng_api_common.viewsets import CheckQueryParamsMixin

from brc.datamodel.models import Besluit, BesluitInformatieObject

from .audits import AUDIT_BRC
from .data_filtering import ListFilterByAuthorizationsMixin
from .filters import BesluitFilter, BesluitInformatieObjectFilter
from .kanalen import KANAAL_BESLUITEN
from .permissions import BesluitAuthScopesRequired, BesluitRelatedAuthScopesRequired
from .scopes import (
    SCOPE_BESLUITEN_AANMAKEN,
    SCOPE_BESLUITEN_ALLES_LEZEN,
    SCOPE_BESLUITEN_ALLES_VERWIJDEREN,
    SCOPE_BESLUITEN_BIJWERKEN,
)
from .serializers import BesluitInformatieObjectSerializer, BesluitSerializer


@extend_schema_view(
    list=extend_schema(
        summary=_("Alle BESLUITen opvragen."),
        description=_("Deze lijst kan gefilterd wordt met query-string parameters."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifiek BESLUIT opvragen."),
        description=_("Een specifiek BESLUIT opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een BESLUIT aan."),
        description=_(
            "Indien geen identificatie gegeven is, dan wordt deze automatischgegenereerd."
            " Er wordt gevalideerd op:\n"
            "- uniciteit van `verantwoorlijkeOrganisatie` + `identificatie`\n"
            "- geldigheid `verantwoorlijkeOrganisatie` RSIN\n"
            " - geldigheid `besluittype` URL - de resource moet opgevraagd kunnen\n"
            "   worden uit de Catalogi API en de vorm van een BESLUITTYPE hebben.\n"
            "- geldigheid `zaak` URL - de resource moet opgevraagd kunnen worden\n"
            "  uit de Zaken API en de vorm van een ZAAK hebben.\n"
            "- `datum` in het verleden of nu\n"
            "- publicatie `besluittype` - `concept` moet `false` zijn \n"
        ),
    ),
    update=extend_schema(
        summary=_("Werk een BESLUIT in zijn geheel bij."),
        description=_(
            "Er wordt gevalideerd op: \n"
            "- uniciteit van `verantwoorlijkeOrganisatie` + `identificatie`\n"
            "- geldigheid `verantwoorlijkeOrganisatie` RSIN\n"
            " - het `besluittype` mag niet gewijzigd worden\n"
            " - geldigheid `zaak` URL - de resource moet opgevraagd kunnen worden\n"
            "uit de Zaken API en de vorm van een ZAAK hebben.\n"
            "- `datum` in het verleden of nu\n"
            "- publicatie `besluittype` - `concept` moet `false` zijn\n"
        ),
    ),
    partial_update=extend_schema(
        summary=_("Werk een BESLUIT deels bij."),
        description=_(
            "Er wordt gevalideerd op:\n"
            " - uniciteit van `verantwoorlijkeOrganisatie` + `identificatie`\n"
            " - geldigheid `verantwoorlijkeOrganisatie` RSIN\n"
            "- het `besluittype` mag niet gewijzigd worden\n"
            "- geldigheid `zaak` URL - de resource moet opgevraagd kunnen worden"
            "  uit de Zaken API en de vorm van een ZAAK hebben.\n"
            " - `datum` in het verleden of nu\n"
            " - publicatie `besluittype` - `concept` moet `false` zijn\n"
        ),
    ),
    destroy=extend_schema(
        summary=_("Verwijder een BESLUIT."),
        description=_(
            " Verwijder een BESLUIT samen met alle gerelateerde resources binnen deze API."
            " **De gerelateerde resources zijn** \n"
            "- `BESLUITINFORMATIEOBJECT`\n"
            "- audit trail regels"
        ),
    ),
)
class BesluitViewSet(
    NotificationViewSetMixin,
    CheckQueryParamsMixin,
    AuditTrailViewsetMixin,
    ListFilterByAuthorizationsMixin,
    viewsets.ModelViewSet,
):
    queryset = Besluit.objects.all().order_by("-pk")
    serializer_class = BesluitSerializer
    filterset_class = BesluitFilter
    lookup_field = "uuid"
    pagination_class = PageNumberPagination
    permission_classes = (BesluitAuthScopesRequired,)
    required_scopes = {
        "list": SCOPE_BESLUITEN_ALLES_LEZEN,
        "retrieve": SCOPE_BESLUITEN_ALLES_LEZEN,
        "create": SCOPE_BESLUITEN_AANMAKEN,
        "destroy": SCOPE_BESLUITEN_ALLES_VERWIJDEREN,
        "update": SCOPE_BESLUITEN_BIJWERKEN,
        "partial_update": SCOPE_BESLUITEN_BIJWERKEN,
    }
    notifications_kanaal = KANAAL_BESLUITEN
    audit = AUDIT_BRC
    global_description = _("Opvragen en bewerken van BESLUITen.")


@extend_schema_view(
    list=extend_schema(
        summary=_("Alle BESLUIT-INFORMATIEOBJECT relaties opvragen."),
        description=_("Deze lijst kan gefilterd wordt met query-string parameters."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifieke BESLUIT-INFORMATIEOBJECT relatie opvragen."),
        description=_("Een specifieke BESLUIT-INFORMATIEOBJECT relatie opvragen."),
    ),
    create=extend_schema(
        summary=_("Maak een BESLUIT-INFORMATIEOBJECT relatie aan."),
        description=_(
            "Registreer een INFORMATIEOBJECT bij een BESLUIT. "
            "Er worden twee types van relaties met andere objecten gerealiseerd:\n"
            "\n**Er wordt gevalideerd op**\n"
            " - geldigheid `besluit` URL\n"
            " - geldigheid `informatieobject` URL\n"
            "- de combinatie `informatieobject` en `besluit` moet uniek zijn\n"
            " - `informatieobject.informatieobjecttype` moet in het ZTC gerelateerd zijn"
            " aan `besluit.besluittype`\n"
            "\n**Opmerkingen**\n"
            " - De `registratiedatum` wordt door het systeem op 'NU' gezet. De"
            " `aardRelatie` wordt ook door het systeem gezet.\n"
            " - Bij het aanmaken wordt ook in de Documenten API de gespiegelde relatie"
            " aangemaakt, echter zonder de relatie-informatie.\n"
        ),
    ),
    update=extend_schema(
        summary=_("Werk een BESLUIT-INFORMATIEOBJECT relatie in zijn geheel bij."),
        description=_(
            "Je mag enkel de gegevens van de relatie bewerken, en niet de relatie zelf"
            "aanpassen.\n"
            " **Er wordt gevalideerd op**"
            "  - `informatieobject` URL en `besluit` URL mogen niet veranderen"
        ),
    ),
    partial_update=extend_schema(
        summary=_("Werk een BESLUIT-INFORMATIEOBJECT relatie deels bij."),
        description=_(
            "Je mag enkel de gegevens van de relatie bewerken, en niet de relatie zelf"
            "aanpassen.\n"
            "**Er wordt gevalideerd op**"
            "- `informatieobject` URL en `besluit` URL mogen niet veranderen"
        ),
    ),
    destroy=extend_schema(
        summary=_("Verwijder een BESLUIT-INFORMATIEOBJECT relatie."),
        description=_("Verwijder een BESLUIT-INFORMATIEOBJECT relatie."),
    ),
)
class BesluitInformatieObjectViewSet(
    NotificationCreateMixin,
    NotificationDestroyMixin,
    AuditTrailCreateMixin,
    AuditTrailDestroyMixin,
    CheckQueryParamsMixin,
    ListFilterByAuthorizationsMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    queryset = BesluitInformatieObject.objects.all()
    serializer_class = BesluitInformatieObjectSerializer
    filterset_class = BesluitInformatieObjectFilter
    lookup_field = "uuid"
    permission_classes = (BesluitRelatedAuthScopesRequired,)
    required_scopes = {
        "list": SCOPE_BESLUITEN_ALLES_LEZEN,
        "retrieve": SCOPE_BESLUITEN_ALLES_LEZEN,
        "create": SCOPE_BESLUITEN_AANMAKEN,
        "destroy": SCOPE_BESLUITEN_ALLES_VERWIJDEREN,
        "update": SCOPE_BESLUITEN_BIJWERKEN,
        "partial_update": SCOPE_BESLUITEN_BIJWERKEN,
    }
    notifications_kanaal = KANAAL_BESLUITEN
    notifications_main_resource_key = "besluit"
    audit = AUDIT_BRC
    global_description = _(
        "Opvragen en bewerken van BESLUIT-INFORMATIEOBJECT relaties."
    )

    def get_queryset(self):
        qs = super().get_queryset()

        # Do not display BesluitInformatieObjecten that are marked to be deleted
        cache = caches["drc_sync"]
        marked_bios = cache.get("bios_marked_for_delete")
        if marked_bios:
            return qs.exclude(uuid__in=marked_bios)
        return qs


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="besluit_uuid",
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description=_("Unieke resource identifier (UUID4)"),
            required=True,
        )
    ]
)
@extend_schema_view(
    list=extend_schema(
        summary=_("Alle audit trail regels behorend bij het BESLUIT."),
        description=_("Alle audit trail regels behorend bij het BESLUIT."),
    ),
    retrieve=extend_schema(
        summary=_("Een specifieke audit trail regel opvragen."),
        description=_("Een specifieke audit trail regel opvragen."),
    ),
)
class BesluitAuditTrailViewSet(AuditTrailViewSet):
    main_resource_lookup_field = "besluit_uuid"
    global_description = _("Opvragen van de audit trail regels.")

    def initialize_request(self, request, *args, **kwargs):
        # workaround for drf-nested-viewset injecting the URL kwarg into request.data
        return super(viewsets.ReadOnlyModelViewSet, self).initialize_request(
            request, *args, **kwargs
        )
