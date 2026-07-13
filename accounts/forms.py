from django import forms

from members.models import Address


class LoginForm(forms.Form):

    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            
            attrs={
                "class": "form-control w-full",
                ":type": "hide_password ? 'password' : 'text'",
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
            "street": forms.TextInput(attrs={"class": "form-control"}),
            "number": forms.TextInput(attrs={"class": "form-control", "max": 3}),
            "neighborhood": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "zipcode": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "max": 8,
                    "x-mask": "99999-999",
                    "placeholder": "00000-000",
                }
            ),
        }
