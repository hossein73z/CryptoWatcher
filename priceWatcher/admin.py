from django.contrib import admin

from priceWatcher.models import Pair


class PairAdmin(admin.ModelAdmin):
    list_display = ('id', 'currency', 'base', 'price', 'price_date')


# Register your models here.
admin.site.register(Pair, PairAdmin)
