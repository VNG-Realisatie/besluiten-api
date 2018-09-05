import uuid as _uuid

from django.db import models

from zds_schema.fields import RSINField


class Besluit(models.Model):
    uuid = models.UUIDField(default=_uuid.uuid4)

    identificatie = models.CharField('identificatie', max_length=50)
    verantwoordelijke_organisatie = RSINField('verantwoordelijke organisatie')

    besluittype = models.URLField('besluittype', help_text="Referentie naar het BESLUITTYPE")
    zaak = models.URLField(
        'zaak', blank=True,  # een besluit kan niet bij een zaak horen (zoals raadsbesluit)
        help_text="Referentie naar de ZAAK waarvan dit besluit uitkomst is"
    )

    datum = models.DateField('datum')
    toelichting = models.TextField('toelichting', blank=True)
    ingangsdatum = models.DateField('ingangsdatum')
    vervaldatum = models.DateField('vervaldatum', null=True, blank=True)
    publicatiedatum = models.DateField('publicatiedatum', null=True, blank=True)
    verzenddatum = models.DateField('verzenddatum', null=True, blank=True)
    uiterlijke_reactiedatum = models.DateField('uiterlijke reactiedatum', null=True, blank=True)

    class Meta:
        verbose_name = 'besluit'
        verbose_name_plural = 'besluiten'
        unique_together = (
            ('identificatie', 'verantwoordelijke_organisatie'),
        )

    def __str__(self):
        return f"{self.verantwoordelijke_organisatie} - {self.identificatie}"
