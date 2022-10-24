from django.conf import settings

from notifications_api_common.kanalen import Kanaal

from brc.datamodel.models import Besluit

KANAAL_BESLUITEN = Kanaal(
    settings.NOTIFICATIONS_KANAAL,
    main_resource=Besluit,
    kenmerken=("verantwoordelijke_organisatie", "besluittype"),
)
