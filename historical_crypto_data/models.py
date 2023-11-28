# create database which will store historical data for crypto currencies.
# create table which will store historical data for crypto currencies.
# create a model for the table.

# Path: historical_crypto_data/models.py

from django.db import models, connections

connection = connections['default']


# Create your models here.
class HistoricalCryptoData(models.Model):
    date = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    market_cap = models.FloatField()
    slug = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.slug
