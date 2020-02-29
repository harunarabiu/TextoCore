from django.shortcuts import render
from django.http import JsonResponse
from account.models import Account, AuthToken, User, Country, Verification
from django.views.decorators.csrf import csrf_exempt

from django.utils.crypto import get_random_string
from otp.OTP import OTP


# Create your views here.


@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        print(request.POST)
        phone = request.POST.get('phone', False)
        token = request.POST.get('token', False)

        if phone and token:
            try:
                token = AuthToken.objects.get(token=token, is_active=True)
                if not token.is_active:
                    print("Token:" + token.token)
                    return JsonResponse({
                        'ok': False,
                        'error_message': "Token is Disabled"
                    })
                else:
                    otp = OTP(user=token.user, phone=phone)
                    if otp.send_otp():
                        return JsonResponse({
                            'ok': True,
                            'error_message': "OTP sent Successfully."
                        })
                    else:
                        return JsonResponse({
                            'ok': False,
                            'error_message': "Sending OTP failed."
                        })

            except AuthToken.DoesNotExist:

                return JsonResponse({
                    'ok': False,
                    'error_message': "Invalid Token"
                })

        else:
            return JsonResponse({
                'ok': False,
                'error_message': "All fields are required."
            })

    else:
        return JsonResponse({
            'ok': True
        })


@csrf_exempt
def resend_otp(request):

    if request.method == "POST":
        phone = request.POST.get('phone', False)
        token = request.POST.get('token', False)

        if phone and token:

            try:
                token = AuthToken.objects.get(token=token, is_active=True)
                if not token.is_active:
                    return JsonResponse({
                        'ok': False,
                        'error_message': "Token is Disabled"
                    })
                else:
                    otp = OTP(user=token.user, phone=phone, retry=True)
                    if otp.retry():
                        return JsonResponse({
                            'ok': True,
                            'error_message': "OTP resend successfully."
                        })
                    else:
                        return JsonResponse({
                            'ok': False,
                            'error_message': "OTP resend Failed."
                        })

            except AuthToken.DoesNotExist:

                return JsonResponse({
                    'ok': False,
                    'error_message': "Invalid Token"
                })
        else:
            return JsonResponse({
                'ok': False,
                'error_message': "All fields are required."
            })
    else:
        return JsonResponse({
            'ok': True,
        })

@csrf_exempt
def verify_otp(request):

    if request.method == "POST":
        phone = request.POST.get('phone', False)
        token = request.POST.get('token', False)
        otp_code = request.POST.get('otp', False)
        print("here here here")
        if phone and token and otp_code:
            print("here here here")
            try:
                token = AuthToken.objects.get(token=token, is_active=True)
                if not token.is_active:
                    print("Token:" + token.token)
                    return JsonResponse({
                        'ok': False,
                        'error_message': "Token is Disabled"
                    })
                else:
                    otp = OTP(user=token.user, phone=phone, otp_code=otp_code, )
                    if otp.verify():
                        return JsonResponse({
                            'ok': True,
                            'error_message': "OTP verification Successfully."
                        })
                    else:
                        #TODO: OTP expired response;
                        return JsonResponse({
                            'ok': False,
                            'error_message': "Wrong  OTP."
                        })

            except AuthToken.DoesNotExist:

                return JsonResponse({
                    'ok': False,
                    'error_message': "Invalid Token"
                })
        else:
            return JsonResponse({
                'ok': False,
                'error_message': "All fields are required."
            })
    else:
        return JsonResponse({
            'ok': True,
        })
