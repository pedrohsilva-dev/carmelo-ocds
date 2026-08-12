from django import forms
from carmel.models import Carmel


class CarmelForm(forms.ModelForm):
    class Meta:
        model = Carmel
        fields = [
            "name",
            "description",
            "city",
            "diocese",
            "price_contribution_default",
            "pay_day_contribution_default",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do Carmelo"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Descrição da comunidade Carmelita..."}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Itapetininga"}),
            "diocese": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Diocese de Itapetininga"}),
            "price_contribution_default": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Valor padrão de contribuição (ex: 50.00)"}
            ),
            "pay_day_contribution_default": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Dia do mês (ex: 10)"}
            ),
        }
