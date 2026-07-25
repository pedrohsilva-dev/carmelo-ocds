from django import forms

from members.models import Address, Phone


class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = [
            "name",
            "number",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Celular, Casa, Trabalho",
                }
            ),
            "number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(00) 00000-0000",
                    "x-mask": "(99) 99999-9999",
                }
            ),
        }


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
            "street": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "number": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "neighborhood": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "2",
                }
            ),
            "zipcode": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "00000-000",
                    "x-mask": "99999-999",
                }
            ),
        }
