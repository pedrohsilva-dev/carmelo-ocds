import datetime

from django.core.mail import send_mail

from django.http import HttpResponse
from django.shortcuts import render, redirect

from accounts.forms import AddressForm, LoginForm

from django.urls import reverse
from django.db import transaction

from django.contrib.auth import authenticate, get_user
from django.contrib.auth import login as login_auth
from django.contrib.auth import logout as logout_auth

from django.utils import timezone
from datetime import datetime

from django.contrib.auth.decorators import login_required

from accounts.models import ResetPasswordAccess
from members.models import Address, Member, Phone
from contributions.models import Contribution
from votes.models import Vote


from django.contrib import messages
from django.shortcuts import get_object_or_404, resolve_url

# Create your views here.


def login(request):
    form_login = LoginForm()

    if request.method == "POST":
        form_login = LoginForm(request.POST)
        if form_login.is_valid():

            user = authenticate(
                request,
                username=form_login.cleaned_data["email"],
                password=form_login.cleaned_data["password"],
            )
            if user:
                login_auth(request, user)
                messages.success(request, "Bem vindo ao sistema OCDS")
            else:
                messages.error(request, "Erro ao Logar tente Novamente")

    return render(request, "login.html", {"form": form_login})


@login_required
def logout(request):
    logout_auth(request)

    return redirect(reverse("login"))


@login_required
def profile(request):
    phones = Phone.objects.filter(member=request.user)
    votes = Vote.objects.filter(member=request.user).all()
    contribution = Contribution.objects.filter(member=request.user).last()

    try:
        address = request.user.address
        address_form = AddressForm(instance=address)
    except:
        address = None
        address_form = AddressForm()

    return render(
        request,
        "profile.html",
        {
            "phones": phones,
            "address_form": address_form,
            "votes": votes,
            "contributions": contribution,
            "address": address,
        },
    )


@login_required
def register_phone(request):

    name_field = request.POST.get("name")
    phone_field = request.POST.get("phone")

    phone_exist = Phone.objects.filter(member=request.user, number=phone_field).first()

    if not phone_exist:

        with transaction.atomic():
            phone = Phone()

            phone.name = name_field
            phone.number = phone_field
            phone.member = request.user

            phone.save()
            messages.success(request, "O Número foi cadastrado com sucesso")
    else:
        messages.error(request, "O Numero Já existe")

    phones = Phone.objects.filter(member=request.user)

    return render(request, "list_contacts.html", {"phones": phones})


@login_required
def delete_phone(request, id):
    with transaction.atomic():

        phone = Phone.objects.filter(id=id, member=request.user).first()
        if phone:
            phone.delete()

        phones = Phone.objects.filter(member=request.user)

    return render(request, "list_contacts.html", {"phones": phones})


@login_required
def register_address(request):

    user: Member = request.user

    form = AddressForm(request.POST)

    if form.is_valid():
        with transaction.atomic():
            address: Address = form.save(commit=False)
            address.member = user  # type: ignore
            address.save()
            user.save()
            messages.success(request, "Endereço cadastrado com sucesso!")

            form = AddressForm(instance=address)

    return render(
        request,
        "location.html",
        {
            "address_form": form,
            "address": request.user.address,
            "status_location": "create",
        },
    )


@login_required
def edit_address(request):
    address = request.user.address
    form = AddressForm(instance=address)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                messages.success(request, "Endereço atualizado com sucesso!")

    return render(
        request,
        "location.html",
        {"address_form": form, "status": "update", "address": address},
    )


@login_required
def delete_address(request):

    form = AddressForm()

    with transaction.atomic() as response_atomic:

        request.user.address.delete()
        address = None
        messages.success(request, "Endereço deletado com sucesso!")

    if address:
        messages.error(request, "Erro ao deletar endereço!")

    return render(request, "location.html", {"address_form": form, "address": address})


def forgot_password(request):
    message = "Se o emeil foi encontrado, foi enviado a url de reset de senha"
    email = request.POST.get("email_forgot")
    with transaction.atomic():
        member = get_object_or_404(Member, email=email)

        if member:
            access = ResetPasswordAccess.objects.filter(member=member).first()
            if access:
                if access.expired_at:
                    if timezone.make_aware(datetime.now()) > access.expired_at:
                        access.delete()
                    else:
                        print("Token ainda valido")
                        send_mail("Reset de senha", f"http://localhost:8000/accounts/reset_password/{access.token}", member.email, ["pedrohenriquedasilva204@gmail.com"])  # type: ignore
                        return render(
                            request, "forgot_password.html", {"message": message}
                        )

            try:

                reset_password = ResetPasswordAccess()
                reset_password.member = member
                reset_password.save()
                send_mail("Reset de senha", f"http://localhost:8000/accounts/reset_password/{reset_password.token}", member.email, ["pedrohenriquedasilva204@gmail.com"])  # type: ignore
            except:
                ...

    return render(request, "forgot_password.html", {"message": message})


def reset_password(request, token):

    access = get_object_or_404(ResetPasswordAccess, token=token)

    if access.expired_at:
        if timezone.make_aware(datetime.now()) > access.expired_at:
            messages.error(request, "Token expirado")
            access.delete()

            return redirect(reverse("login"))

    if request.method == "POST":
        password1 = request.POST.get("password")
        password2 = request.POST.get("confirm_password")
        if password1 == password2:
            member = access.member

            member.set_password(password1)

            member.save()

            access.delete()

            return redirect(reverse("login"))

    return render(request, "reset_password.html", {"token": token})
