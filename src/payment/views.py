from django.shortcuts import render
from account.models import User, Account

# Create your views here.


def index(request, uid=None):

    if uid:
        user = User.objects.get(pk=uid)

    template = "index.html"
    context = None

    return render(request, template, context)
