from django.conf import settings

from vng_api_common.notifications.kanalen import Kanaal

from brc.datamodel.models import Besluit

KANAAL_BESLUITEN = Kanaal(
    settings.NOTIFICATIONS_KANAAL,
    main_resource=Besluit,
    kenmerken=(
        'verantwoordelijke_organisatie',
        'besluittype',
    )
)
