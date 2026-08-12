from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import Member


class EmailBackend(ModelBackend):

    def authenticate(self, request, identifier=None, password=None, **kwargs):
        """Autentica um membro por e-mail OU nome (o admin usa 'username').

        O campo `name` é único no modelo, então a busca é segura.
        """

        if not identifier:
            return None

        # O Django envia o valor em `username` em alguns caminhos (admin)
        identifier = identifier or kwargs.get("username")

        try:
            user = Member.objects.get(
                Q(email__iexact=identifier) | Q(name__iexact=identifier)
            )
        except (Member.DoesNotExist, Member.MultipleObjectsReturned):
            return None

        if user.check_password(password):  # type: ignore
            return user

        return None

    def get_user(self, user_id):
        try:
            return Member.objects.get(pk=user_id)
        except Member.DoesNotExist:
            return None
