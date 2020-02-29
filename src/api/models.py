from django.db import models
from django.conf import settings

# Create your models here.

DELIVERY_STATUS_CHOICE = [("UNKNOWN", "Unknown"),
                          ("ACKED", "Aknowledge"),
                          ("ENROUTE", "Enroute"),
                          ("DELIVRD", "Delivered"),
                          ("EXPIRED", "Expired"),
                          ("DELETED", "Deleted"),
                          ("UNDELIV", "Undelivered"),
                          ("ACCEPTED", "Accepted"),
                          ("REJECTD", "Rejected")]


User = settings.AUTH_USER_MODEL


class Message(models.Model):
    msg_user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    msg_sender = models.CharField(max_length=11)
    msg_destination = models.TextField()
    msg_message = models.TextField()
    msg_status = models.CharField(max_length=11, default="SENT")
    msg_channel = models.CharField(max_length=11, default="API")
    msg_type = models.CharField(max_length=11, default="Text")
    is_scheduled = models.BooleanField(default=False)
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


class DeliveryReport(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=13)
    msg_id = models.CharField(max_length=255)
    response_code = models.CharField(max_length=25)
    status = models.CharField(
        max_length=255, choices=DELIVERY_STATUS_CHOICE, default="SENT")
    cost_sms = models.DecimalField(decimal_places=4, max_digits=5, default=0)
    charge = models.DecimalField(decimal_places=4, max_digits=5, default=0)
    MCC_MNC = models.CharField(max_length=25)
    error_code = models.CharField(max_length=25)
    tag_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
