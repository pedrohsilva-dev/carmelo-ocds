from django import forms

from members.models import Address


class LoginForm(forms.Form):

    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "seu.email@carmelo.org"}),
        required=True,
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control w-full",
                ":type": "hide_password ? 'password' : 'text'",
                "placeholder": "Digite sua senha",
            }
        ),
        label="Senha",
        required=True,
    )


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "street",
            "number",
            "neighborhood",
            "city",
            "state",
            "zipcode",
        ]

        widgets = {
            "street": forms.TextInput(attrs={"class": "form-control", "placeholder": "Rua / Avenida / Logradouro"}),
            "number": forms.TextInput(attrs={"class": "form-control", "max": 3, "placeholder": "Nº"}),
            "neighborhood": forms.TextInput(attrs={"class": "form-control", "placeholder": "Bairro"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "UF (ex: SP)"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cidade"}),
            "zipcode": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "max": 8,
                    "x-mask": "99999-999",
                    "placeholder": "00000-000",
                }
            ),
        }
