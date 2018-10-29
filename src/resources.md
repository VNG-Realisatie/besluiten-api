# Resources

Dit document beschrijft de (RGBZ-)objecttypen die als resources ontsloten
worden met de beschikbare attributen.


## Besluit

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/besluit)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| identificatie | Identificatie van het besluit binnen de organisatie die het besluit heeft vastgesteld. | string | nee | C​R​U​D |
| verantwoordelijkeOrganisatie | Het RSIN van de Niet-natuurlijk persoon zijnde de organisatie die het besluit heeft vastgesteld. | string | ja | C​R​U​D |
| besluittype | Aanduiding van de aard van het BESLUIT. Referentie naar het BESLUITTYPE in de zaaktypecatalogus. | string | ja | C​R​U​D |
| zaak | Referentie naar de ZAAK waarvan dit besluit uitkomst is | string | nee | C​R​U​D |
| datum | De beslisdatum (AWB) van het besluit. | string | ja | C​R​U​D |
| toelichting | Toelichting bij het besluit. | string | nee | C​R​U​D |
| bestuursorgaan | Een orgaan van een rechtspersoon krachtens publiekrecht ingesteld of een persoon of college, met enig openbaar gezag bekleed onder wiens verantwoordelijkheid het besluit vastgesteld is. | string | nee | C​R​U​D |
| ingangsdatum | Ingangsdatum van de werkingsperiode van het besluit. | string | ja | C​R​U​D |
| vervaldatum | Datum waarop de werkingsperiode van het besluit eindigt. | string | nee | C​R​U​D |
| vervalreden |  | string | nee | C​R​U​D |
| vervalredenWeergave |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| publicatiedatum | Datum waarop het besluit gepubliceerd wordt. | string | nee | C​R​U​D |
| verzenddatum | Datum waarop het besluit verzonden is. | string | nee | C​R​U​D |
| uiterlijkeReactiedatum | De datum tot wanneer verweer tegen het besluit mogelijk is. | string | nee | C​R​U​D |

## BesluitInformatieObject

Objecttype op [GEMMA Online](https://www.gemmaonline.nl/index.php/Rgbz_2.0/doc/objecttype/besluitinformatieobject)

| Attribuut | Omschrijving | Type | Verplicht | CRUD* |
| --- | --- | --- | --- | --- |
| url |  | string | nee | ~~C~~​R​~~U~~​~~D~~ |
| informatieobject | URL-referentie naar het informatieobject waarin (een deel van) het besluit beschreven is. | string | ja | C​R​U​D |


* Create, Read, Update, Delete
