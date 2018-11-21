===========
Wijzigingen
===========

0.4.0 (2018-11-21)
==================

Autorisatie-feature release

* Voeg JWT client/secret management toe
* Opzet credentialstore om URLs te kunnen valideren met auth/autz

0.3.0 (2018-11-19)
==================

Aanpassingen na RGBZ-toetsing

Features
--------

* ``CORS``-support toegevoegd

Breaking changes
----------------

* ``Besluit.datum`` als datum in plaats van datetime
* Geen limitatie op lengte van ``Besluit.toelichting``
* ``identificatie`` en ``verantwoorelijkeOrganisatie`` zijn immutable
* ``vervalredenWeergave`` is niet langer een enum - de mapping staat in de
  beschrijving van ``vervalreden``.


0.2.1 (2018-10-25)
==================

Bugfix in infrastructuur

* nodejs deps toegevoegd (swagger2openapi)

0.2.0 (2018-10-02)
==================

Besluit-informatieobject relatie resource toegevoegd

* fix MIME-types voor error responses
* ``besluitinfomratieobject`` als nested resource toegevoegd op besluiten
* validaties op ``BesluitInformatieObject`` toegevoegd

0.1.1 (2018-09-12)
==================

* Fix missing ``Accept-Crs`` header in ZAAK-url validator
* Added license


0.1.0 (2018-09-10)
==================

* Eerste aanzet besluitregistratie
