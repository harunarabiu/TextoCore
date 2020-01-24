from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL
# Create your models here.


class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # change otp to otp_code
    otp = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    retry_count = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    expiry = models.DateTimeField()
    expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
