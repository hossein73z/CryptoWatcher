from django.db import models


class Pair(models.Model):
    id = models.IntegerField(primary_key=True)
    currency = models.TextField(null=False)
    base = models.TextField(null=False)
    price = models.IntegerField(null=False, default=0)
    price_date = models.DateTimeField(null=False)

    class Meta:
        db_table = 'pairs'
