import os
import logging
import requests
from api.helper import format_date

from django.utils.datastructures import MultiValueDictKeyError
from requests.exceptions import ConnectionError

from django.contrib.auth import authenticate, get_user_model


from django.shortcuts import render, HttpResponse, HttpResponse, Http404, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_datetime

from django.http import JsonResponse
from django.conf import settings
from .models import Message, Response, DeliveryReport
from account.models import Account, AuthToken, User, Country, Verification

from api.models import Message

from api.SMS import SMS

# User = get_user_model()


# Create your views here.
LOW_BALANCE = 2
USER = None


@csrf_exempt
def entry(request):

    required_keys = ['token', 'sender', 'message', 'to', 'type', 'dlr']
    received_key = []
    response = {}

    if request.method == "GET":

        # valid indidual key
        #### check keys with empty values ####
        for key, value in request.GET.items():
            if key in required_keys and value == '':
                return JsonResponse({
                    'ok': False,
                    'error_code': 1101,
                    'error_message': 'All fields are required.'
                })
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
                'error_message': 'All fields are required.'
            })
        else:
            logging.info('all keys are valid')

        ### AUTHENTICATE TOKEN && CHECK BALANCE###
        try:
            _token = request.GET.get('token', False)
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

    elif request.method == "POST":

        #### check keys with empty values ####
        for key, value in request.POST.items():
            if key in required_keys and value == '':
                return JsonResponse({
                    'ok': False,
                    'error_code': 1101,
                    'error_message': 'All fields are required'
                })
            else:
                pass

            print(key, value)

            received_key.append(key)

        #### check missing key #####
        missing_keys = set(required_keys).difference(received_key)

        if missing_keys != set():
            print(missing_keys)
            return JsonResponse({
                'ok': False,
                'error_code': 1101,
                'error_message': 'All fields are required.'
            })
        else:
            logging.info('all keys are valid')

        ### AUTHENTICATE TOKEN && CHECK BALANCE###
        try:
            _token = request.POST.get('token', False)
            token = AuthToken.objects.get(token=_token)
            if not token.is_active:
                return JsonResponse({'error': "Invalid Token"})
            print("Token:" + token.token)
        except MultiValueDictKeyError:
            return JsonResponse({'error': "Token is Missing"})
        except AuthToken.DoesNotExist:
            return JsonResponse({'error': "Invalid Token"})

        sender = request.POST.get('sender', False)
        message = request.POST.get('message', False)
        to = request.POST.get('to', False)
        msg_type = request.POST.get('type', False)
        dlr = request.POST.get('dlr', False)

    logging.info("sending...")

    sms = SMS(user=token.user, sender=sender, recipients=to,
              message=message, msg_type=msg_type)

    ### CHECK BALANCE ###
    msg_estimated_cost = sms.cost()
    user_balance = account_balance(user=sms.USER)

    if user_balance > msg_estimated_cost:
        logging.info("sending...")
        sms.send()
    else:
        response["ok"] = False
        response["error_code"] = 1101
        response["error_message"] = "Insufficient Account Balance."
        return JsonResponse(response)
    ### SEND MESSAGE ###

    print("cost: {} pages: {} total Numbers: {}".format(
        sms.cost(),  sms.pages(), sms.total_sent()))
    return JsonResponse(sms.FINAL_RESPONSE)


@csrf_exempt
def UserAuth(request):
    if request.method == "POST":
        username = request.POST.get("username", False)
        password = request.POST.get("password", False)

        if username and password:
            user = authenticate(request, email=username, password=password)

            if user and user.is_active:
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
                        'error_message': 'Not Authorised.'
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
                'error_message': "All fields are required."
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
                first_name=first_name,
                last_name=last_name
            )
            new_user.set_password(password)
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


@csrf_exempt
def SMSHistory(request):

    if request.method == "POST":
        _token = request.POST.get("token", False)

        if _token:
            try:
                token = AuthToken.objects.get(token=_token)
                Messages = Message.objects.filter(msg_user=token.user)

                AllMessages = []

                for message in Messages:
                    message = {
                        "senderid": message.msg_sender,
                        "recipients": message.msg_destination,
                        "message": message.msg_message,
                        "status": message.msg_status,
                        "type": message.msg_type,
                        "cost": message.msg_cost,
                        "date": format_date(date=message.created_at),
                    }

                    AllMessages.append(message)

                response = {
                    "ok": True,
                    "messages": AllMessages
                }

                return JsonResponse(response)

            except AuthToken.DoesNotExist:
                response = {
                    "ok": False,
                    "error_code": 105,
                    "error_message": "Invalid Token"
                }

                return JsonResponse(response)

            except Message.DoesNotExist:
                response = {
                    "ok": True,
                    "messages": ""
                }

                return JsonResponse(response)

        else:
            response = {
                "ok": False,
                "error_code": 105,
                "error_message": "Token is Missing"
            }

            return JsonResponse(response)

    else:
        return Http404()


@csrf_exempt
def DLR(request):

    if request.method == "POST":
        sender = request.POST.get('sSender', False)
        phoneNo = request.POST.get('sMobileNo', False)
        status = request.POST.get('sStatus', False)
        msg_id = request.POST.get('sMessageId', False)
        cost_persms = request.POST.get('iCostPerSms', False)
        charge = request.POST.get('iCharge', False)
        mcc = request.POST.get('iMCCMNC', False)
        error_code = request.POST.get('iErrCode', False)
        tag_name = request.POST.get('sTagName', False)
        sudf1 = request.POST.get('sUdf1', False)
        sudf2 = request.POST.get('sUdf2', False)
        date_done = request.POST.get('dtDone', False)
        date_submit = request.POST.get('dtSubmit', False)

        print(msg_id)

        try:
            Report = DeliveryReport.objects.get(msg_id=msg_id)
            Report.phone_number = phoneNo
            Report.status = status
            Report.cost_sms = cost_persms
            Report.charge = charge
            Report.MCC_MNC = mcc
            Report.error_code = error_code
            Report.tag_name = tag_name

            Report.save()

            with open('dlr.log', 'a') as log:
                report = "{sender} {phoneNo} {status} {msg_id} {cost_persms}  {charge} {mcc} {error_code} {tag_name} {sudf1} {sudf2} {date_done} {date_submit}\n".format(sender=sender,
                                                                                                                                                                         phoneNo=phoneNo,
                                                                                                                                                                         status=status,
                                                                                                                                                                         msg_id=msg_id,
                                                                                                                                                                         cost_persms=cost_persms,
                                                                                                                                                                         charge=charge,
                                                                                                                                                                         mcc=mcc,
                                                                                                                                                                         error_code=error_code,
                                                                                                                                                                         tag_name=tag_name,
                                                                                                                                                                         sudf1=sudf1,
                                                                                                                                                                         sudf2=sudf2,
                                                                                                                                                                         date_done=date_done,
                                                                                                                                                                         date_submit=date_submit)
                log.write(report)

            print(report)
            return HttpResponse("<h3>It Works.</h3>")

        except DeliveryReport.DoesNotExist:
            print("Message Doesn't exist.")

            return HttpResponse("<h3>Wrong Details</h3>")

    else:
        return HttpResponse("<h3>It Works.</h3>")


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


def send_otp():
    pass


def verify_otp():

    pass


def retry_otp():

    pass


# TODO: Create a function to initialise Email and Phone Verification
def send_email_verification(user=None, email=None):
    # TODO: Generate verifcation code
    token = get_random_string(length=32)
    # TODO: Save Verification code to DB

    Verification.objects.create(user=user, email_token=token)

    # TODO: send verification code to email

    pass


def send_phone_verification(phone=None):
    if phone:
        # TODO: Generate verificaton code
        token = get_random_string(6, '0123456789')

        phone = format_phone(country, phone)
        # TODO: Send Verification code via SMS

        # TODO: Save verification Details to DB

        text = f'Texto: Use {token} to verify your phone number'

# TODO: create a function to valid verification code


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
