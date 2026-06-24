from django import forms

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
                attrs={"class": "form-control", "placeholder": "Descrição dos Votos"}
            ),
        }


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote

        fields = ["date", "type", "votes_registration", "year_duration"]

        widgets = {
            "date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "type": forms.Select(
                attrs={"class": "form-control", "x-model": "type_vote"}
            ),
            "year_duration": forms.NumberInput(attrs={"class": "form-control"}),
            "votes_registration": forms.Select(attrs={"class": "form-control"}),
        }
