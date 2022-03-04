from django.contrib import admin
from .models import *


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """ Model Admin de Novidades. """

    fields = ("brief", "url", ("icon", "color"))
    list_display = ("id", "brief")


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """ Model Admin de alertas. """

    fields = [
        "title",
        "description",
        "active",
        "expiration_date",
        "color",
    ]

    list_display = ("title", "active", "expiration_date", "description")
