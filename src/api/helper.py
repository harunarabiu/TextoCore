from django.utils.dateparse import parse_datetime
from account.models import Account


class Verfication():
    def __init__(self, user):

        try:
            account = Account.objects.get(user=user)

        except Exception as e:
            print(e)

        self.EMAIL = user.email
        self.PHONE = account.phone


def format_date(date):
    date_str = parse_datetime(str(date)).strftime("%d-%m-%Y %H:%M:%S")

    return date_str
