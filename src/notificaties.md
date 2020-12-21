## Notificaties
## Berichtkenmerken voor Besluiten API

Kanalen worden typisch per component gedefinieerd. Producers versturen berichten op bepaalde kanalen,
consumers ontvangen deze. Consumers abonneren zich via een notificatiecomponent (zoals <a href="https://notificaties-api.vng.cloud/api/v1/schema/" rel="nofollow">https://notificaties-api.vng.cloud/api/v1/schema/</a>) op berichten.

Hieronder staan de kanalen beschreven die door deze component gebruikt worden, met de kenmerken bij elk bericht.

De architectuur van de notificaties staat beschreven op <a href="https://github.com/VNG-Realisatie/notificaties-api" rel="nofollow">https://github.com/VNG-Realisatie/notificaties-api</a>.


### besluiten

**Kanaal**
`besluiten`

**Main resource**

`besluit`



**Kenmerken**

* `verantwoordelijke_organisatie`: Het RSIN van de niet-natuurlijk persoon zijnde de organisatie die het besluit heeft vastgesteld.
* `besluittype`: URL-referentie naar het BESLUITTYPE (in de Catalogi API).

**Resources en acties**


* <code>besluit</code>: create, update, destroy

* <code>besluitinformatieobject</code>: create, destroy


