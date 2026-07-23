from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Member

# =========================
# REGISTER FORM
# =========================


class MemberForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                ":type": "hide_password ? 'password' : 'text'",
            }
        ),
        label="Senha",
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                ":type": "hide_password ? 'password' : 'text'",
            }
        ),
        label="Confirmar Senha",
    )

    class Meta:
        model = Member
        fields = ["name", "email", "church", "entry_date", "roles"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "church": forms.TextInput(attrs={"class": "form-control"}),
            "entry_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "roles": forms.Select(attrs={"class": "form-control px-1"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if Member.objects.filter(email=email).exists():
            raise forms.ValidationError("Email já cadastrado")

        return email

    # =========================
    # Validação da senha usando
    # AUTH_PASSWORD_VALIDATORS
    # =========================
    def clean_password(self):
        password: str = self.cleaned_data.get("password")  # type: ignore

        try:
            validate_password(password, self.instance)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)  # type: ignore

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if not password:
            self.add_error("password", "A senha é obrigatória.")

        if not password2:
            self.add_error("password2", "Confirme sua senha.")

        if password and password2:

            if password != password2:
                self.add_error("password2", "As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")
        user.set_password(password)

        if commit:
            user.save()

        return user


class MemberChangeForm(forms.ModelForm):

    password = forms.CharField(
        required=False,
        label="Nova Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                ":type": "hide_password ? 'password' : 'text'",
            }
        ),
    )

    password2 = forms.CharField(
        required=False,
        label="Confirmar Nova Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                ":type": "hide_password ? 'password' : 'text'",
            }
        ),
    )

    class Meta:
        model = Member
        fields = [
            "name",
            "email",
            "church",
            "entry_date",
            "roles",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "church": forms.TextInput(attrs={"class": "form-control"}),
            "entry_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "roles": forms.Select(
                attrs={
                    "class": "form-control px-1",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if Member.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")

        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if not password:
            return password

        validate_password(password, self.instance)

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        # Não alterou senha
        if not password and not password2:
            return cleaned_data

        # Apenas um campo preenchido
        if not password or not password2:
            if not password:
                self.add_error("password", "Preencha o campo 1 de senha.")
            if not password2:
                self.add_error("password2", "Preencha o campo 2 de senha.")
            raise ValidationError("Preencha os dois campos de senha.")

        if password != password2:
            raise ValidationError("As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        member = super().save(commit=False)

        password = self.cleaned_data.get("password")

        if password:
            member.set_password(password)

        if commit:
            member.save()

        return member
