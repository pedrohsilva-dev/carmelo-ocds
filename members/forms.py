from django import forms

from .models import Member

# =========================
# REGISTER FORM
# =========================


class MemberForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Senha"
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
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

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("As senhas não coincidem")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")
        user.set_password(password)

        if commit:
            user.save()

        return user


class MemberChangeForm(forms.ModelForm):

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
