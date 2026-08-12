# form Add contribution
from datetime import date

from django import forms

from contributions.models import Contribution

# Valor máximo aceito em uma única contribuição
MAX_CONTRIBUTION = 100_000.00


class ContributionForm(forms.ModelForm):

    # Opcional: vazio → a view usa o valor padrão do carmelo
    price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Valor (ex: 50.00)",
                "step": "0.01",
                "min": "0.01",
            }
        ),
    )

    class Meta:
        model = Contribution

        fields = [
            "date_pay",
            "price",
        ]

        widgets = {
            "date_pay": forms.DateInput(
                # format ISO obrigatório: input HTML5 type="date" exige
                # YYYY-MM-DD, senão (com pt-BR) o navegador mostra vazio
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "placeholder": "Data do pagamento",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        # Membro de referência para validações de data
        self.member = kwargs.pop("member", None)
        super().__init__(*args, **kwargs)

    def clean_price(self):
        price = self.cleaned_data.get("price")

        # Preço vazio → o carmelo usa o valor padrão (definido na view)
        if price is None or price == "":
            return None

        if price <= 0:
            raise forms.ValidationError(
                "O valor da contribuição deve ser maior que zero."
            )

        if price > MAX_CONTRIBUTION:
            raise forms.ValidationError(
                f"O valor máximo permitido é R$ {MAX_CONTRIBUTION:,.2f}."
            )

        return price

    def clean_date_pay(self):
        date_pay = self.cleaned_data.get("date_pay")

        if date_pay is None:
            raise forms.ValidationError("Informe a data do pagamento.")

        if date_pay > date.today():
            raise forms.ValidationError(
                "Não é permitido registrar contribuições futuras."
            )

        entry_date = getattr(self.member, "entry_date", None)
        if isinstance(entry_date, str):
            entry_date = date.fromisoformat(entry_date)

        if entry_date:
            if date_pay < entry_date:
                raise forms.ValidationError(
                    "Não é permitido registrar contribuições antes da entrada do membro."
                )

        return date_pay
