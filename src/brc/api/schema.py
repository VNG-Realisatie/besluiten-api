from django.conf import settings

from drf_yasg import openapi
from vng_api_common.notifications.utils import notification_documentation

from .kanalen import KANAAL_BESLUITEN

description = f"""Een API om een besluitregistratiecomponent (BRC) te benaderen.

Een BESLUIT wordt veelal schriftelijk vastgelegd maar dit is niet
noodzakelijk. Omgekeerd kan het voorkomen dat in een INFORMATIEOBJECT meerdere
besluiten vastgelegd zijn. Vandaar de N:M-relatie naar INFORMATIEOBJECT. Een
besluit komt voort uit een zaak van de zaakbehandelende organisatie dan wel is
een besluit van een andere organisatie dat het onderwerp (object) is van een
zaak van de zaakbehandelende organisatie. BESLUIT heeft dan ook een optionele
relatie met de ZAAK waarvan het een uitkomst is.

De typering van BESLUITen is in de Catalogi API (ZTC) ondergebracht in de vorm
van BESLUITTYPEn.

**Afhankelijkheden**

Deze API is afhankelijk van:

* Catalogi API
* Notificaties API
* Documenten API *(optioneel)*
* Zaken API *(optioneel)*
* Autorisaties API *(optioneel)*

**Autorisatie**

Deze API vereist autorisatie. Je kan de
[token-tool](https://zaken-auth.vng.cloud/) gebruiken om JWT-tokens te
genereren.

### Notificaties

{notification_documentation(KANAAL_BESLUITEN)}

**Handige links**

* [Documentatie]({settings.DOCUMENTATION_URL}/standaard)
* [Zaakgericht werken]({settings.DOCUMENTATION_URL})
"""

info = openapi.Info(
    title=f"{settings.PROJECT_NAME} API",
    default_version=settings.API_VERSION,
    description=description,
    contact=openapi.Contact(
        email="standaarden.ondersteuning@vng.nl", url=settings.DOCUMENTATION_URL
    ),
    license=openapi.License(
        name="EUPL 1.2", url="https://opensource.org/licenses/EUPL-1.2"
    ),
)
