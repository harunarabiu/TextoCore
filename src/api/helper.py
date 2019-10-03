from .models import Account


class Verfication():
    def __init__(self, user):

        try:
            account = Account.objects.get(user=user)

        except Exception as e:
            print(e)

        self.EMAIL = user.email
        self.PHONE = account.phone
