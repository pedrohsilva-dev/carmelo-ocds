from django import forms
from django.utils import timezone

from votes.models import Vote, VotesRegistration


class VoteRegisterForm(forms.ModelForm):
    class Meta:
        model = VotesRegistration

        fields = [
            "name",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome do voto"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descrição dos Votos",
                    "rows": 3,
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Informe o nome do voto.")

        if (
            VotesRegistration.objects.filter(name__iexact=name)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Já existe um voto com este nome.")

        return name


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote

        fields = ["date", "type", "votes_registration", "year_duration"]

        widgets = {
            "date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                    "placeholder": "Data e hora do voto",
                }
            ),
            "type": forms.Select(
                attrs={"class": "form-control", "x-model": "type_vote"}
            ),
            "year_duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Duração em anos",
                    "min": 1,
                    "max": 99,
                }
            ),
            "votes_registration": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_date(self):
        date_value = self.cleaned_data.get("date")

        if date_value is None:
            raise forms.ValidationError("Informe a data e hora do voto.")

        if timezone.is_naive(date_value):
            date_value = timezone.make_aware(date_value)

        if date_value > timezone.now():
            raise forms.ValidationError("Não é permitido registrar votos no futuro.")

        return date_value

    def clean_year_duration(self):
        vote_type = self.cleaned_data.get("type")
        year_duration = self.cleaned_data.get("year_duration")

        if vote_type == "TEMP" and not year_duration:
            raise forms.ValidationError(
                "Votos temporários precisam de uma duração em anos."
            )

        if year_duration and year_duration <= 0:
            raise forms.ValidationError("A duração deve ser maior que zero.")

        return year_duration
