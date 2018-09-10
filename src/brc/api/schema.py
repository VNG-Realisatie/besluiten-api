from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

info = openapi.Info(
    title="Besluitregistratiecomponent (brc) API",
    default_version='1',
    description="Een API om een besluitregistratiecomponent te benaderen",
    contact=openapi.Contact(
        email="support@maykinmedia.nl",
        url="https://github.com/VNG-Realisatie/gemma-zaken"
    ),
    license=openapi.License(name="EUPL 1.2"),
)

schema_view = get_schema_view(
    # validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)
