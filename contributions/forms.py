# form Add contribution
from django import forms

from contributions.models import Contribution


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution

        fields = [
            "date_pay",
            "price",
        ]

        widgets = {
            "date_pay": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }
