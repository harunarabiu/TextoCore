from api.views import SMS
from .models import Otp
from django.utils.crypto import get_random_string
from django.utils import timezone
import datetime


class OTP():

    def __init__(self, user=None, phone=None, otp_code=None, otp_length=6, otp_template=None, retry=False):
        self.user = user
        self.phone = phone
        self.otp_code = otp_code
        self.otp_length = otp_length
        self.otp_template = "Your Texto verication code is {otp_code}"
        self.otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=10)
        self.gen_otp_code = get_random_string(self.otp_length, '0123456789')

        # Retry
        if retry:
            try:
                otp = Otp.objects.filter(
                    phone=self.phone, expired=False, verified=False).last()

                self.gen_otp_code = otp.otp

            except Otp.DoesNotExist:
                pass

        self.otp_msg = self.otp_template.format(otp_code=self.gen_otp_code)

    def send_otp(self):
        if self.phone:
            sms = SMS(user=self.user, sender="Texto",
                      recipients=self.phone, message=self.otp_msg)
            sms.send()

            print(self.user)
            Otp.objects.create(
                user=self.user, phone=self.phone, otp=self.gen_otp_code, expiry=self.otp_expiry)

            return True
        else:
            return False

    def verify(self):

        try:
            otp = Otp.objects.get(
                phone=self.phone, otp=self.otp_code, expired=False, verified=False)

            if otp:
                print(otp.expiry)
                print(timezone.now())
                if timezone.now() <= otp.expiry:
                    if otp.otp == str(self.otp_code):
                        otp.verified = True
                        otp.save()
                        return True
                    else:
                        return False
                        # wrong Otp
                        print("wrong100  otp")
                else:

                    otp.expired = True
                    otp.save()
                    # otp expired
                    print("otp expired")
                    return False

            else:
                # wrong otp
                print("wrong otp")
                return False

        except Otp.DoesNotExist:
            # wrong otp
            print("wrong otp")
            return False

    def retry(self):

        try:
            print("try")
            otp = Otp.objects.filter(
                phone=self.phone, expired=False, verified=False).last()
            print(otp)
            if otp:

                print(otp.expiry)
                print(timezone.now())

                # TODO: check retry count
                sms = SMS(user=self.user, sender="Texto",
                          recipients=self.phone, message=self.otp_msg)
                sms.send()

                print(self.user)

                otp.retry_count = otp.retry_count + 1
                otp.expiry = self.otp_expiry
                otp.save()

                return True

            else:
                # wrong otp
                print("wrong otp")
                return False

        except Otp.DoesNotExist:
            # wrong otp
            print("wrong otppppp")
            return False
