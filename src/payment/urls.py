from django.contrib import admin
from django.urls import path, include
from .views import index

urlpatterns = [
    path('', index, name="index"),
    path('<str:uid>/', index, name="index"),

]
