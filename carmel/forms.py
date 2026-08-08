from django import forms
from carmel.models import Carmel


class CarmelForm(forms.ModelForm):
    class Meta:
        model = Carmel
        fields = [
            "name",
            "description",
            "price_contribution_default",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do Carmelo"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Descrição da comunidade Carmelita..."}),
            "price_contribution_default": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Valor padrão de contribuição (ex: 50.00)"}
            ),
        }
