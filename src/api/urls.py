"""TextoCore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import entry, UserAuth, BalanceCheck, NewAccount, SMSHistory, DLR

urlpatterns = [
    path('sms/send/', entry, name="entry"),
    path('sms/history/', SMSHistory, name="history"),
    path('sms/dlr/', DLR, name="deliveryreport"),
    path('account/auth/', UserAuth, name="uauth"),
    path('account/balance/', BalanceCheck, name="balancecheck"),
    path('account/new/', NewAccount, name="newaccount"),
]
