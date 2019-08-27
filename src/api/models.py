from django.db import models
from django.conf import settings

# Create your models here.


User = settings.AUTH_USER_MODEL


class Message(models.Model):
    msg_user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    msg_sender = models.CharField(max_length=11)
    msg_destination = models.TextField()
    msg_message = models.TextField()
    msg_status = models.CharField(max_length=11, default="SENT")
    msg_channel = models.CharField(max_length=11, default="API")
    msg_type = models.CharField(max_length=11, default="TEXT")
    msg_schedule = models.CharField(max_length=255, blank=True)
    msg_cost = models.FloatField()

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.id)


class Response(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=13)
    msg_id = models.CharField(max_length=255)
    response_code = models.CharField(max_length=25)

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
