from django.db import models
from account.models import Country
# Create your models here.


class Operator(models.Model):
    name = models.CharField(max_length=125, blank=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    MNC = models.IntegerField(blank=False)
    MCC = models.IntegerField(blank=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name_plural = 'Operators'

    def __str__(self):
        return str(self.name)
        
class Currency(models.Model):
    name = models.CharField(max_length=125, blank=False)
    symbol = models.CharField(max_length=10, blank=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

class Plan(models.Model):
    name = models.CharField(max_length=125, blank=False)
    charge = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)


class Price(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    price = models.FloatField(max_length=30, blank=False)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)


class PricingOperator(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    price = models.ManyToManyField(Price, blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        pass


class PricingCountry(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    price = models.ManyToManyField(Price, blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        pass


# TODO: create Charge model for Charges Variation in different Countries



