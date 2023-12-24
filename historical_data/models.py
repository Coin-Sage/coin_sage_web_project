# create database which will store historical data for crypto currencies.
# create table which will store historical data for crypto currencies.
# create a model for the table.

from django.db import models, connections

connection = connections['historical_data']


# Create your models here.
class HistoricalData(models.Model):
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


def create_model(name):
    class Meta:
        app_label = 'historical_data'
        db_table = name

    return type(name, (models.Model,), {
        '__module__': __name__,
        'date': models.DateTimeField(),
        'open': models.FloatField(),
        'high': models.FloatField(),
        'low': models.FloatField(),
        'close': models.FloatField(),
        'volume': models.FloatField(),
        'market_cap': models.FloatField(),
        'slug': models.CharField(max_length=255),
        'Meta': Meta,
            }
        )

class HistoricalDatatest(models.Model):
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