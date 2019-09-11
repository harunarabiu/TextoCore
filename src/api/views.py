import os
import logging
import requests


from django.utils.datastructures import MultiValueDictKeyError
from requests.exceptions import ConnectionError

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.shortcuts import render, HttpResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

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
            logging.info('all keys are valid')

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

        sender = request.GET['sender']
        message = request.GET['message']
        to = request.GET['to']
        msg_type = request.GET['type']
        dlr = request.GET['dlr']

        sms = SMS(user=token.user, sender=sender, recipients=to,
                  message=message, msg_type=msg_type)

        ### CHECK BALANCE ###
        msg_estimated_cost = sms.cost()
        user_balance = account_balance(user=sms.USER)
        if user_balance > msg_estimated_cost:
            sms.send()
        else:
            return JsonResponse({'error': "Insuffient Account Balance."})
        ### SEND MESSAGE ###

        print("cost: {} pages: {} total Numbers: {}".format(
            sms.cost(),  sms.pages(), sms.total_sent()))
        return JsonResponse(sms.FINAL_RESPONSE)

    else:
        return Http404()


@csrf_exempt
def UserAuth(request):
    if request.method == "POST":
        username = request.POST.get("username", False)
        password = request.POST.get("password", False)

        if username and password:
            user = authenticate(username=username, password=password)

            if user is not None:
                account = AuthToken.objects.get(user=user, is_active=True)
                token = account.token
                response = {
                    "ok": True,
                    "token": token
                }

                return JsonResponse(response)
            else:
                response = {
                    "ok": False,
                    "error_code": 105,
                    "error_message": "Invalid User Credentials."
                }

                return JsonResponse(response)
        else:
            response = {
                "ok": False,
                "error_code": 105,
                "error_message": "Username or Password is Missing."
            }

            return JsonResponse(response)

    else:
        raise Http404()


def account_balance(user=None):
    try:
        account = Account.objects.get(user=user)

        if account.balance > 2:
            return account.balance
        else:
            return 0
        print("current balance:" + str(account.balance))

    except Account.DoesNotExist:
        print("couldn't get Account")


def deduct_unit(user=None, unit=0):
    try:
        account = Account.objects.get(user=user)
        if account.balance >= unit:
            old_balance = account.balance
            new_balance = account.balance - unit
            # update DB
            account.balance = new_balance
            account.book_balance = old_balance
            account.save()

        else:
            raise Exception("Insuffient Balance.")
            return 0

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

        self.SENT = False
        self.STATUS_MESSAGE = None
        self.STATUS_CODE = None

        self.COST = self.cost()

        self.NO_RECIPIENTS = 0

        self.FINAL_RESPONSE = {
            "ok": True,
            "error_code": self.STATUS_CODE,
            "error_message": self.STATUS_MESSAGE,
            "sender": self.sender,
            "message": self.message,
            "price": self.COST,
            "results": []
        }

        print(self.sender, self.recipients, self.message, self.msg_type)

    def send(self):
        try:
            endpoint = settings.SMS_SEND_API + "source={sender}&destination={recipients}&type=1&message={message}&dlr={msg_type}".format(
                sender=self.sender, recipients=self.recipients, message=self.message, msg_type=self.msg_type)
            query = requests.get(endpoint)
            if query.status_code == 200:

                response = query.text.strip()
                self.response = response

                # Saving Message to DB
                user = User.objects.get(pk=1)
                self.MESSAGE = Message.objects.create(msg_user=self.USER, msg_sender=self.sender, msg_destination=self.recipients,
                                                      msg_message=self.message, msg_cost=self.cost(), msg_type=self.msg_type)

                self.handle_bulk_response()

                # Deduct SMS charge from Account

                deduct_unit(user=self.USER, unit=self.COST)

                """

                    {
                        "ok": True,
                        "error_code": None,
                        "error_message": None,
                        "sender": "HMAX",
                        "message": "Hello World",
                        "price": "5.8",
                        "result": [
                            {
                                "to": "2348189931773",
                                "msg_status": "SENT|DELIVERED|DND",
                                "msg_id": "f8fb22cc-d701-44b4-87d1-9f401ea3ca90"
                            }
                        ]
                    }
                """

        except ConnectionError:
            raise Exception("error: Can't Connect to GateAway")

    def handle_bulk_response(self):
        """
            SAMPLE RESPONSE
            1701|2348189931773|f8fb22cc-d701-44b4-87d1-9f401ea3ca90,1701|2348189931773|1a5c4dfb-6695-45ad-9a2a-c084d053f031
        """

        responses = self.response.split(',')

        for response in responses:

            content = response.split('|')
            if len(content) == 3:
                # Change "self.SENT status to True"
                self.SENT = True

                status = content[0]
                phone = content[1]
                msg_id = content[2]

                print(status, phone, msg_id)

                if int(status) == 1701:
                    response_ = {
                        "to": phone,
                        "msg_status": "SENT",
                        "msg_id": msg_id
                    }

                    self.FINAL_RESPONSE["results"].append(response_)

                    self.NUMBERS_SENT.append(phone)
                    print(self.FINAL_RESPONSE)
                    # Save response to DB
                    Response.objects.create(
                        message=self.MESSAGE, phone_number=phone, msg_id=msg_id, response_code=status)

            # "if len(content) == 2" the response is error

            elif len(content) == 2:
                status = content[0]
                phone = content[1]
                if status == '1032':
                    response_ = {
                        "to": phone,
                        "msg_status": "ON_DND",
                    }
                    self.FINAL_RESPONSE["results"].append(response_)

                    self.NUMBERS_ON_DND.append(phone)
                elif status == '1706':
                    response_ = {

                        "to": phone,
                        "msg_status": "INVALID_NO",
                    }
                    self.FINAL_RESPONSE["results"].append(response_)
                    self.NUMBERS_INVALID.append(phone)
                elif status == '1710':
                    raise Exception("Internal error.")
                elif status == '1025':
                    raise Exception("Insufficient credit.")
                elif status == '1715':
                    raise Exception("Response timeout.")
                elif status == '1028':
                    raise Exception("Spam message.")
            else:
                print(content)

    def save_reponse(self):
        pass

    def total_sent(self):
        total = (len(self.NUMBERS_SENT) + len(self.NUMBERS_SENT_DND))

        return int(total)

    def total_recipients(self):
        recipients = self.recipients.split(",")
        total_recipients = len(recipients)
        return total_recipients

    def pages(self):
        count = len(self.message)/160 if (len(self.message) %
                                          160) == 0 else int(len(self.message)/160) + 1
        return int(count)

    def cost(self):
        pages = self.pages()
        no_recipients = self.total_sent() if self.SENT else self.total_recipients()
        cost = pages * 1.85 * no_recipients

        return cost

    def total_chars(self):
        count = len(self.message)
        return int(count)
