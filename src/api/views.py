import os
import requests

from django.utils.datastructures import MultiValueDictKeyError
from requests.exceptions import ConnectionError

from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, HttpResponse, Http404
from django.http import JsonResponse
from django.conf import settings
from .models import Message, Response
from account.models import Account, AuthToken


# Create your views here.
LOW_BALANCE = 2
USER = None


def entry(request):

    if request.method == "GET":

        required_keys = ['token', 'sender', 'message', 'to', 'type', 'dlr']
        received_key = []

        # valid indidual key
        #### check keys with empty values ####
        for key, value in request.GET.items():
            if key in required_keys and value == '':
                return JsonResponse({key: 700})
            else:
                pass

            received_key.append(key)

        #### check missing key #####
        missing_keys = set(required_keys).difference(received_key)

        if missing_keys is set():
            return JsonResponse({'missing': str(missing_keys)})
        else:
            print('all keys are valid')

        ### AUTHENTICATE TOKEN && CHECK BALANCE###
        try:
            _token = request.GET['token']
            token = AuthToken.objects.get(token=_token)
            if not token.is_active:
                return JsonResponse({'error': "Invalid Token"})
            print("Token:" + token.token)
        except MultiValueDictKeyError:
            return JsonResponse({'error': "Token is Missing"})
        except AuthToken.DoesNotExist:
            return JsonResponse({'error': "Invalid Token"})

        ### CHECK BALANCE ###
        check_balance(user=USER)
        ### SEND MESSAGE ###

        sender = request.GET['sender']
        message = request.GET['message']
        to = request.GET['to']
        msg_type = request.GET['type']
        dlr = request.GET['dlr']

        sms = SMS(user=token.user, sender=sender, recipients=to,
                  message=message, msg_type=msg_type)

        sms.send()

        print("cost: {} pages: {} total Numbers: {}".format(
            sms.cost(),  sms.pages(), sms.total_sent()))
        return HttpResponse("hellow")

    else:
        return Http404()


def check_balance(user=None):
    try:
        account = Account.objects.get(user=user)

        if account.balance > 2:
            return account.balance
        else:
            return 0
        print("current balance:" + str(account.balance))

    except Account.DoesNotExist:
        print("couldn't get Account")


class SMS():

    def __init__(self, user=None, sender=None, recipients=None, message=None, msg_type='Text'):
        self.sender = sender.strip()
        self.recipients = recipients
        self.message = message.strip()
        self.response = None
        self.msg_type = 0 if msg_type == 'Text' else 1

        self.MESSAGE = None
        self.USER = user
        self.NUMBERS_SENT = []
        self.NUMBERS_SENT_DND = []
        self.NUMBERS_ON_DND = []
        self.NUMBERS_INVALID = []
        self.REPONSES = []

        print(self.sender, self.recipients, self.message, self.msg_type)

    def send(self):
        try:
            endpoint = settings.SMS_SEND_API + "source={sender}&destination={recipients}&type=1&message={message}&dlr={msg_type}".format(
                sender=self.sender, recipients=self.recipients, message=self.message, msg_type=self.msg_type)
            query = requests.get(endpoint)
            if query.status_code == 200:

                # Saving Message to DB
                user = User.objects.get(pk=1)
                self.MESSAGE = Message.objects.create(msg_user=self.USER, msg_sender=self.sender, msg_destination=self.recipients,
                                                      msg_message=self.message, msg_cost=self.cost(), msg_type=self.msg_type)

                response = query.text.strip()
                self.response = response

            self.handle_bulk_response()
        except ConnectionError:
            print("error: Can't Connect to GateAway")

    def handle_bulk_response(self):
        responses = self.response.split(',')

        for response in responses:

            content = response.split('|')
            if len(content) == 3:
                status = content[0]
                phone = content[1]
                msg_id = content[2]
                print(status, phone, msg_id)

                if int(status) == 1701:
                    self.NUMBERS_SENT.append(phone)
                    Response.objects.create(
                        message=self.MESSAGE, phone_number=phone, msg_id=msg_id, response_code=status)

            elif len(content) == 2:
                status = content[0]
                phone = content[1]
                if status == '1032':
                    self.NUMBERS_ON_DND.append(phone)
                if status == '1706':
                    self.NUMBERS_INVALID.append(phone)
            else:
                print(content)

    def save_reponse(self):
        pass

    def total_sent(self):
        total = (len(self.NUMBERS_SENT) + len(self.NUMBERS_SENT_DND))

        return int(total)

    def pages(self):
        count = len(self.message)/160 if (len(self.message) %
                                          160) == 0 else int(len(self.message)/160) + 1
        return int(count)

    def cost(self):
        pages = self.pages()
        print(pages)
        cost = pages * 1.85 * self.total_sent()

        return cost

    def total_chars(self):
        count = len(self.message)
        return int(count)
