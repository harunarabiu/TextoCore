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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


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
