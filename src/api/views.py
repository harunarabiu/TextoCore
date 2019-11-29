import os
import logging
import requests


from django.utils.datastructures import MultiValueDictKeyError
from requests.exceptions import ConnectionError

from django.contrib.auth import authenticate

from django.shortcuts import render, HttpResponse, HttpResponse, Http404, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string

from django.http import JsonResponse
from django.conf import settings
from .models import Message, Response
from account.models import Account, AuthToken, User, Country, Verification


# Create your views here.
LOW_BALANCE = 2
USER = None

@csrf_exempt
def entry(request):

    if request.method == "GET":

        required_keys = ['token', 'sender', 'message', 'to', 'type', 'dlr']
        received_key = []
        response = {}

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

        if missing_keys != set():
            print(missing_keys)
            return JsonResponse({
                'ok': False,
                'error_code': 1101,
                'error_msg': 'All fields are required.'
            })
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

        sender = request.GET.get('sender', False)
        message = request.GET.get('message', False)
        to = request.GET.get('to', False)
        msg_type = request.GET.get('type', False)
        dlr = request.GET.get('dlr', False)

        sms = SMS(user=token.user, sender=sender, recipients=to,
                  message=message, msg_type=msg_type)

        ### CHECK BALANCE ###
        msg_estimated_cost = sms.cost()
        user_balance = account_balance(user=sms.USER)
        if user_balance > msg_estimated_cost:
            sms.send()
        else:
            response["error_code"] = 1101
            response["error_message"] = "Insuffient Account Balance."
            return JsonResponse(response)
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
            user = User.objects.get(email=username, password=password)


            if user:
                print(user.id,user.email)
                try:
                    account = AuthToken.objects.get(user=user, is_active=True)
                    token = account.token
                    response = {
                        "ok": True,
                        "token": token
                    }

                    return JsonResponse(response)
                except AuthToken.DoesNotExist:
                    response = {
                        'ok': False,
                        'error_code': 1105,
                        'error_msg': 'Not Authorised.'
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


@csrf_exempt
def NewAccount(request):
    if request.method == "POST":

        required_keys = ['first_name', 'last_name',
                         'email', 'password', 'phone', 'country']
        received_key = []
        response = {}

        # valid indidual key
        #### check keys with empty values ####
        for key, value in request.POST.items():
            print(request.POST)

            if key in required_keys and value == '':
                return JsonResponse({key: 700})
            else:
                pass

            received_key.append(key)

        #### check missing key #####
        missing_keys = set(required_keys).difference(received_key)

        if missing_keys != set():
            for item in missing_keys:
                print(item)

            return JsonResponse({
                'ok': False,
                'error': 100,
                'error_msg': "All fields are required."
            })
        else:
            print("all keys are valid")


        

        email = request.POST.get("email", False)
        password = request.POST.get("password", False)
        first_name = request.POST.get("first_name", False)
        last_name = request.POST.get("last_name", False)
        _phone = request.POST.get("phone", False)
        _country = request.POST.get("country", False)
        country = Country.objects.get(name=_country)
        phone = format_phone(country=_country, phone=_phone)

        try:
            user_exist = User.objects.get(email=email)
            
            response = {
                "ok": False,
                "error_code": 1101,
                "error_message": "Email is already Registered."
            }

            return JsonResponse(response)

        except User.DoesNotExist:
            user_exist = None

        # Create User

        try:

            new_user = User.objects.create(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            new_user.save()

            if Account.objects.filter(user=new_user) is None:
                account = Account.objects.create(
                    user=new_user,
                    phone=phone,
                    country=country
                )

            else:
                account = Account.objects.get(user=new_user)
                account.phone = phone
                account.country = country
                account.save()

            print(new_user)

            response = {
                "ok": True,
                "error_code": None,
                "error_message": None
            }

            return JsonResponse(response)

        except Exception as e:
            print(e)

            response = {
                "ok": False,
                "error_code": 105,
                "error_message": "Can't create User."
            }

            return JsonResponse(response)

    else:
        raise Http404()


@csrf_exempt
def BalanceCheck(request):
    if request.method == "POST":
        _token = request.POST.get("token", False)

        if _token:
            try:
                token = AuthToken.objects.get(token=_token, is_active=True)
                account = Account.objects.get(user=token.user)
                balance = round(account.balance, 2)
                response = {
                    "ok": True,
                    "balance": balance
                }

                return JsonResponse(response)

            except AuthToken.DoesNotExist:
                response = {
                    "ok": False,
                    "error_code": 105,
                    "error_message": "Invalid Token."
                }

                return JsonResponse(response)
        else:
            response = {
                "ok": False,
                "error_code": 105,
                "error_message": "Token is Missing."
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


#TODO: Create a function to initialise Email and Phone Verification
def send_email_verification(user=None, email=None):
    #TODO: Generate verifcation code
    token = get_random_string(length=32)
    #TODO: Save Verification code to DB
    
    Verification.objects.create(user=user, email_token=token)

    #TODO: send verification code to email

    pass


def send_phone_verification(phone=None):
    if phone:
        #TODO: Generate verificaton code
        token = get_random_string(6, '0123456789')

        phone = format_phone(country, phone)
        #TODO: Send Verification code via SMS


        #TODO: Save verification Details to DB

        text = f'Texto: Use {token} to verify your phone number'

#TODO: create a function to valid verification code

def phone_verification_Validation(phone=None, code=None):

    pass

def email_verification_validation(email=None, code=None):

    pass

def format_phone(country=None, phone=None):
    try:
        country = Country.objects.get(name=country)
        if len(phone) >= 11:
            phone = phone[1:]

        return f'{country.CCC}{phone}'

    except Country.DoesNotExist:
        return phone



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
