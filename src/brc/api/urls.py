from django.conf.urls import url
from django.urls import include, path

from vng_api_common import routers
from vng_api_common.views import SchemaViewAPI, SchemaViewRedoc

from .viewsets import (
    BesluitAuditTrailViewSet,
    BesluitInformatieObjectViewSet,
    BesluitViewSet,
)

router = routers.DefaultRouter()
router.register(
    "besluiten",
    BesluitViewSet,
    [routers.nested("audittrail", BesluitAuditTrailViewSet)],
)
router.register("besluitinformatieobjecten", BesluitInformatieObjectViewSet)

# TODO: the EndpointEnumerator seems to choke on path and re_path

urlpatterns = [
    url(
        r"^v(?P<version>\d+)/",
        include(
            [
                # API documentation
                url(
                    r"^schema/openapi.yaml",
                    SchemaViewAPI.as_view(),
                    name="schema",
                ),
                url(
                    r"^schema/",
                    SchemaViewRedoc.as_view(url_name="schema-redoc"),
                    name="schema-redoc",
                ),
                # actual API
                url(r"^", include(router.urls)),
                # should not be picked up by drf-yasg
                path("", include("vng_api_common.api.urls")),
            ]
        ),
    )
]
