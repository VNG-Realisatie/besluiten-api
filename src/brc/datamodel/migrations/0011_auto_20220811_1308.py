# Generated by Django 2.2.8 on 2022-08-11 13:08

from django.db import migrations, models
import vng_api_common.fields


class Migration(migrations.Migration):

    dependencies = [
        ("datamodel", "0010_migrate_to_flattened_urls"),
    ]

    operations = [
        migrations.AlterField(
            model_name="besluit",
            name="besluittype",
            field=models.URLField(
                help_text="URL-referentie naar het BESLUITTYPE (in de Catalogi API).",
                verbose_name="besluittype",
            ),
        ),
        migrations.AlterField(
            model_name="besluit",
            name="verantwoordelijke_organisatie",
            field=vng_api_common.fields.RSINField(
                help_text="Het RSIN van de niet-natuurlijk persoon zijnde de organisatie die het besluit heeft vastgesteld.",
                max_length=9,
                verbose_name="verantwoordelijke organisatie",
            ),
        ),
        migrations.AlterField(
            model_name="besluit",
            name="zaak",
            field=models.URLField(
                blank=True,
                help_text="URL-referentie naar de ZAAK (in de Zaken API) waarvan dit besluit uitkomst is.",
                verbose_name="zaak",
            ),
        ),
        migrations.AlterField(
            model_name="besluitinformatieobject",
            name="informatieobject",
            field=models.URLField(
                help_text="URL-referentie naar het INFORMATIEOBJECT (in de Documenten API) waarin (een deel van) het besluit beschreven is.",
                max_length=1000,
                verbose_name="informatieobject",
            ),
        ),
    ]
