from account.models import Verification
from django.http import JsonResponse


def phone_verification(function):
    def wrap(request, *args, **kwargs):
        ver = Verification.objects.get(user=request.user)
        if ver.phone:
            return function(request, *args, **kwargs)
        else:
            response = {
                "ok": False,
                "error_code": 105,
                "error_message": "Phone number not verified"
            }
            return JsonResponse(response)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
