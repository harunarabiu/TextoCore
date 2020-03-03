from django.db import models

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.utils.crypto import get_random_string
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

#token = get_random_string(length=32)
# Create your models here.
#User = settings.AUTH_USER_MODEL


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):

        user = self.create_user(
            email,
        )
        user.set_password(password)
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):

        user = self.create_user(
            email,
        )
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.first_name == '' and self.last_name == '':
            return '{0}'.format(self.email)
        return '{0} ({1})'.format(self.get_full_name(), self.email)

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def staff(self):
        "Is the user a member of staff?"
        return self.is_staff

    @property
    def admin(self):
        "Is the user a member of staff?"
        return self.is_admin


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


class Account(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    book_balance = models.FloatField(default=0)
    balance = models.FloatField(default=0.0)
    phone = models.CharField(max_length=13, blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.user.email)


class AuthToken(models.Model):
    # TODO: Change user = models.OneToOneField to ForeignKey
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.token


class Verification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.BooleanField(default=False)
    phone_token = models.CharField(max_length=255)
    email = models.BooleanField(default=False)
    email_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)


### Signals ###


@receiver(post_save, sender=User)
def create_Account(sender, instance, created, *args, **kwargs):
    if created:
        try:
            Account.objects.create(user=instance)
        except Exception as e:
            print(e)


@receiver(post_save, sender=User)
def genarate_user_token(sender, instance, created, *args, **kwargs):
    if created:
        try:
            token = get_random_string(length=32)
            AuthToken.objects.create(
                user=instance, token=token, is_active=True)
        except:
            pass


@receiver(post_save, sender=User)
def create_Verification(sender, instance, created, *args, **kwargs):
    if created:
        try:
            phone_token = get_random_string(
                length=6, allowed_chars='0123456789')
            email_token = get_random_string(length=35)
            print('verification created')
            Verification.objects.create(
                user=instance, phone_token=phone_token, email_token=email_token)
        except Exception as e:
            print(e)


@receiver(pre_save, sender=Account)
def update_Verification(sender, instance, *args, **kwargs):
    # TODO: get changes from email and phone

    try:
        account = Account.objects.get(user=instance.id)
        phone = account.phone

        if phone is not instance.phone:
            phone_token = get_random_string(
                length=6, allowed_chars='0123456789')

            verification = Verification.objects.get(user=instance.user)
            verification.phone = False
            phone_token = get_random_string(
                length=6, allowed_chars='0123456789')

            verification.phone_token = phone_token
            verification.save()

    except Exception as e:
        print(e)
