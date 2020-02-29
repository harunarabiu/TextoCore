import os
import logging
import requests
from api.helper import format_date

from django.utils.datastructures import MultiValueDictKeyError
from requests.exceptions import ConnectionError

from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_datetime

from django.http import JsonResponse
from django.conf import settings
from .models import Message, Response, DeliveryReport
from account.models import Account, AuthToken, User, Country, Verification

from api.models import Message


class SMS():

    def __init__(self, user=None, sender=None, recipients=None, message=None, msg_type='text'):
        self.sender = sender.strip()
        self.recipients = recipients
        self.message = message.strip()
        self.response = None
        self.msg_type = 0 if msg_type.lower() == 'text' else 1

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
            "date": "",
            "results": []
        }

        print(self.sender, self.recipients, self.message, self.msg_type)

    def send(self):
        try:
            endpoint = settings.SMS_SEND_API + "source={sender}&destination={recipients}&type={msg_type}&message={message}&dlr=1".format(
                sender=self.sender, recipients=self.recipients, message=self.message, msg_type=self.msg_type)
            query = requests.get(endpoint)
            logging.info(endpoint)
            if query.status_code == 200:
                response = query.text.strip()
                self.response = response

                # Saving Message to DB
                user = User.objects.get(pk=1)
                self.MESSAGE = Message.objects.create(msg_user=self.USER, msg_sender=self.sender, msg_destination=self.recipients,
                                                      msg_message=self.message, msg_cost=self.cost(), msg_type=self.msg_type)

                self.FINAL_RESPONSE["date"] = self.format_date(
                    self.MESSAGE.created_at)

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
            print("error: Can't Connect to GateAway")
            raise Exception("error: Can't Connect to GateAway")
        except Exception as e:
            print(e)

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
                    DeliveryReport.objects.create(
                        message=self.MESSAGE, phone_number=phone, msg_id=msg_id, response_code=status)

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
                    print("Internal error.")

                elif status == '1025':
                    print("Insufficient credit.")

                elif status == '1715':
                    print("Response timeout.")

                elif status == '1028':
                    print("Spam message.")

            else:
                print(content)

    def single_response(self):
        pass

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

    def format_date(self, date):
        date_str = parse_datetime(str(date)).strftime("%d-%m-%Y %H:%M:%S")

        return date_str
