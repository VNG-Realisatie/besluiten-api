# Generated by Django 2.0.13 on 2019-05-28 09:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0006_auto_20181119_0828'),
    ]

    operations = [
        migrations.AddField(
            model_name='besluitinformatieobject',
            name='aard_relatie',
            field=models.CharField(choices=[('hoort_bij', 'Hoort bij, omgekeerd: kent'), ('legt_vast', 'Legt vast, omgekeerd: kan vastgelegd zijn als')], default='', max_length=20, verbose_name='aard relatie'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='besluitinformatieobject',
            name='informatieobject',
            field=models.URLField(help_text='URL-referentie naar het informatieobject waarin (een deel van) het besluit beschreven is.', max_length=1000, verbose_name='informatieobject'),
        ),
        migrations.AlterField(
            model_name='besluitinformatieobject',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, help_text='Unieke resource identifier (UUID4)', unique=True),
        ),
    ]
