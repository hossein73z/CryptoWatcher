import datetime

from django.db import models
from django.utils.timezone import make_aware


class Pair(models.Model):
    id = models.IntegerField(primary_key=True)
    currency = models.TextField(null=False)
    base = models.TextField(null=False)
    price = models.FloatField(null=False, default=0)
    price_date = models.DateTimeField(null=False, default=make_aware(datetime.datetime.now()))

    class Meta:
        db_table = 'pairs'
