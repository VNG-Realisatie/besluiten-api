from django.contrib import admin

from .models import Besluit


@admin.register(Besluit)
class BesluitAdmin(admin.ModelAdmin):
    list_display = ('verantwoordelijke_organisatie', 'identificatie', 'datum')
    list_filter = ('datum', 'ingangsdatum')
    date_hierarchy = 'datum'
    search_fields = ('verantwoordelijke_organisatie', 'identificatie', 'besluittype', 'zaak')
