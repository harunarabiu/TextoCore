from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.db.models.signals import post_save
from django.dispatch import receiver

#token = get_random_string(length=32)
# Create your models here.
User = settings.AUTH_USER_MODEL


class Account(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    book_balance = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    phone = models.CharField(max_length=13, blank=True)

    def __str__(self):
        return str(self.user.username)


class AuthToken(models.Model):
    # TODO: Change user = models.OneToOneField to ForeignKey
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.token


class Country(models.Model):
    name = models.CharField(max_length=125, unique=True)
    CCC = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name_plural = 'Countries'

    def __str__(self):
        return str(self.name)


### Signals ###

@receiver(post_save, sender=User)
def create_Account(sender, instance, created, *args, **kwargs):
    if created:
        try:
            Account.objects.create(user=instance)
        except:
            pass


@receiver(post_save, sender=User)
def genarate_user_token(sender, instance, created, *args, **kwargs):
    if created:
        try:
            token = get_random_string(length=32)
            AuthToken.objects.create(user=instance, token=token)
        except:
            pass
