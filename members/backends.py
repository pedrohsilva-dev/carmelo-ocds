from django.contrib.auth.backends import ModelBackend
from .models import Member


class EmailBackend(ModelBackend):

    def authenticate(self, request, email=None, password=None, **kwargs):

        # o admin manda username → aqui vira email

        try:
            user = Member.objects.get(email=email)
        except Member.DoesNotExist:
            return None

        if user.check_password(password):  # type: ignore
            return user

        return None
