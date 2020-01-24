from django.contrib import admin
from django.urls import path, include
from .views import send_otp, verify_otp

urlpatterns = [
    path('', send_otp, name="send_otp"),
    path('verify/', verify_otp, name="verify_otp"),
]
