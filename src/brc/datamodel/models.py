import uuid as _uuid

from django.db import models

from zds_schema.fields import RSINField
from zds_schema.validators import (
    UntilNowValidator, alphanumeric_excluding_diacritic
)

from .constants import VervalRedenen


class Besluit(models.Model):
    uuid = models.UUIDField(default=_uuid.uuid4)

    identificatie = models.CharField(
        'identificatie', max_length=50, default=_uuid.uuid4,
        validators=[alphanumeric_excluding_diacritic],
        help_text="Identificatie van het besluit binnen de organisatie die "
                  "het besluit heeft vastgesteld."
    )
    verantwoordelijke_organisatie = RSINField(
        'verantwoordelijke organisatie',
        help_text="Het RSIN van de Niet-natuurlijk persoon zijnde de "
                  "organisatie die het besluit heeft vastgesteld."
    )

    besluittype = models.URLField(
        'besluittype',
        help_text="Aanduiding van de aard van het BESLUIT. Referentie naar het "
                  "BESLUITTYPE in de zaaktypecatalogus."
    )
    zaak = models.URLField(
        'zaak', blank=True,  # een besluit kan niet bij een zaak horen (zoals raadsbesluit)
        help_text="Referentie naar de ZAAK waarvan dit besluit uitkomst is"
    )

    datum = models.DateTimeField(
        'datum', validators=[UntilNowValidator()],
        help_text="De beslisdatum (AWB) van het besluit."
    )
    toelichting = models.TextField(
        'toelichting', blank=True, max_length=1000,
        help_text="Toelichting bij het besluit."
    )

    # TODO: hoe dit valideren? Beter ook objectregistratie en URL referentie?
    # Alleen de namen van bestuursorganen mogen gebruikt
    # worden die voor de desbetrreffende (sic) organisatie van
    # toepassing zijn. Voor een gemeente zijn dit
    # 'Burgemeester', 'Gemeenteraad' en 'College van B&W'.
    # Indien het, bij mandatering, een bestuursorgaan van
    # een andere organisatie betreft dan de organisatie die
    # verantwoordelijk is voor de behandeling van de zaak,
    # dan moet tevens de naam van die andere organisatie
    # vermeld worden (bijvoorbeeld "Burgemeester gemeente
    # Lent").
    bestuursorgaan = models.CharField(
        'bestuursorgaan', max_length=50, blank=True,
        help_text="Een orgaan van een rechtspersoon krachtens publiekrecht "
                  "ingesteld of een persoon of college, met enig openbaar gezag "
                  "bekleed onder wiens verantwoordelijkheid het besluit "
                  "vastgesteld is."
    )

    ingangsdatum = models.DateField(
        'ingangsdatum',
        help_text="Ingangsdatum van de werkingsperiode van het besluit."
    )
    vervaldatum = models.DateField(
        'vervaldatum', null=True, blank=True,
        help_text="Datum waarop de werkingsperiode van het besluit eindigt."
    )
    vervalreden = models.CharField(
        'vervalreden', max_length=30, blank=True,
        choices=VervalRedenen.choices
    )
    publicatiedatum = models.DateField(
        'publicatiedatum', null=True, blank=True,
        help_text="Datum waarop het besluit gepubliceerd wordt."
    )
    verzenddatum = models.DateField(
        'verzenddatum', null=True, blank=True,
        help_text="Datum waarop het besluit verzonden is."
    )
    # TODO: validator
    # Afleidbaar gegeven (uit BESLUITTYPE.Reactietermijn en
    # BESLUIT.Besluitdatum)
    # .. note: (rekening houdend met weekend- en feestdagen
    uiterlijke_reactiedatum = models.DateField(
        'uiterlijke reactiedatum', null=True, blank=True,
        help_text="De datum tot wanneer verweer tegen het besluit mogelijk is."
    )

    class Meta:
        verbose_name = 'besluit'
        verbose_name_plural = 'besluiten'
        unique_together = (
            ('identificatie', 'verantwoordelijke_organisatie'),
        )

    def __str__(self):
        return f"{self.verantwoordelijke_organisatie} - {self.identificatie}"


class BesluitInformatieObject(models.Model):
    """
    Aanduiding van het (de) INFORMATIEOBJECT(en) waarin
    het BESLUIT beschreven is.

    Besluiten worden veelal schriftelijk vastgelegd maar kunnen ook mondeling
    genomen zijn. Deze relatie verwijst naar het informatieobject waarin het
    besluit is vastgelegd, indien van toepassing. Mogelijkerwijs is het besluit in
    meerdere afzonderlijke informatieobjecten vastgelegd of zijn in één
    informatieobject meerdere besluiten vastgelegd.
    """
    uuid = models.UUIDField(default=_uuid.uuid4)

    besluit = models.ForeignKey(
        'besluit', on_delete=models.CASCADE,
        help_text="URL-referentie naar het BESLUIT."
    )
    informatieobject = models.URLField(
        'informatieobject',
        help_text="URL-referentie naar het informatieobject waarin (een deel van) "
                  "het besluit beschreven is."
    )

    class Meta:
        verbose_name = 'besluitinformatieobject'
        verbose_name_plural = 'besluitinformatieobjecten'
        unique_together = (
            ('besluit', 'informatieobject'),
        )

    def __str__(self):
        return str(self.uuid)
