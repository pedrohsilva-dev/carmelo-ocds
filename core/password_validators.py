import re

from django.core.exceptions import ValidationError


class StrongPasswordValidator:

    def validate(self, password, user=None):

        if len(password) < 10:
            raise ValidationError("A senha deve possuir pelo menos 10 caracteres.")

        if not re.search(r"[A-Z]", password):
            raise ValidationError("A senha deve possuir uma letra maiúscula.")

        if not re.search(r"[a-z]", password):
            raise ValidationError("A senha deve possuir uma letra minúscula.")

        if not re.search(r"\d", password):
            raise ValidationError("A senha deve possuir um número.")

        if not re.search(r"[!@#$%^&*()_\-+=<>?/{}[\]|\\.,:;]", password):
            raise ValidationError("A senha deve possuir um caractere especial.")

    def get_help_text(self):
        return (
            "A senha deve possuir no mínimo 10 caracteres, "
            "uma letra maiúscula, uma minúscula, um número "
            "e um caractere especial."
        )
