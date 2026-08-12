from datetime import datetime
import re

from django.contrib import messages
from django.contrib.auth import authenticate, login as login_auth
from django.contrib.auth import logout as logout_auth
from django.contrib.auth.decorators import login_required

# from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

# from django.utils import timezone

from accounts.forms import AddressForm, LoginForm

# from accounts.models import ResetPasswordAccess
from base.utils import paginate
from contributions.services import month_empty
from members.models import Address, Member, Phone
from votes.models import Vote

# Create your views here.


def login(request):
    """Autentica um usuário no sistema por e-mail OU nome.

    Se o usuário já estiver logado, redireciona para o perfil.
    Suporta o parâmetro `next` para voltar à página de origem.
    """
    if request.user.is_authenticated:
        return redirect(reverse("profile"))

    form_login = LoginForm()

    if request.method == "POST":
        form_login = LoginForm(request.POST)
        if form_login.is_valid():
            user = authenticate(
                request,
                identifier=form_login.cleaned_data["identifier"],
                password=form_login.cleaned_data["password"],
            )
            if user:
                login_auth(request, user)
                messages.success(request, f"Bem-vindo(a), {user.get_short_name()}!")

                next_url = request.POST.get("next") or request.GET.get("next")
                if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                    return redirect(next_url)

                return redirect(reverse("profile"))
            else:
                messages.error(request, "Email/Nome ou senha incorretos. Tente novamente.")

    next_url = request.GET.get("next") or request.POST.get("next")
    return render(request, "login.html", {"form": form_login, "next": next_url})


@login_required
def logout(request):
    """Desconecta o usuário autenticado da sessão.

    Limpa a sessão do usuário e redireciona para a página de login.
    """
    logout_auth(request)

    return redirect(reverse("login"))


@login_required
def profile(request):
    """Exibe o perfil do usuário logado.

    Obtém e renderiza: telefones, votos, última contribuição e endereço do usuário.
    """
    phones = Phone.objects.filter(member=request.user)
    votes = paginate(
        Vote.objects.filter(member=request.user)
        .select_related("votes_registration")
        .order_by("-date"),
        request,
        per_page=10,
        page_param="votes_page",
    )

    # Situação das contribuições (meses pagos/faltantes) — agregação única
    contributions = month_empty(request.user)

    # MOSTRAR CONTRIBUIÇÕES NÃO PAGAS

    try:
        address = request.user.address
        address_form = AddressForm(instance=address)
    except AttributeError:
        address = None
        address_form = AddressForm()

    return render(
        request,
        "profile.html",
        {
            "phones": phones,
            "address_form": address_form,
            "votes": votes,
            "contributions": contributions,
            "address": address,
        },
    )


@login_required
def register_phone(request):
    """Registra um novo telefone para o usuário logado.

    Valida se o telefone já existe; se não, cria um novo registro.
    Renderiza a lista de telefones atualizada.
    """
    name_field = request.POST.get("name")
    phone_field = request.POST.get("phone")

    # MANUTENÇÃO: Usar .exists() em vez de .first() para apenas verificar existência
    phone_exist = Phone.objects.filter(member=request.user, number=phone_field).first()

    if not phone_exist:
        with transaction.atomic():
            # MANUTENÇÃO: Usar Phone.objects.create() em vez de criar instância vazia
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
    """Deleta um telefone específico do usuário logado.

    Remove o telefone apenas se pertencer ao usuário autenticado.
    Renderiza a lista de telefones atualizada.
    """
    with transaction.atomic():
        # MANUTENÇÃO: Considerar usar get_object_or_404 com validação de permissão
        phone = Phone.objects.filter(id=id, member=request.user).first()
        if phone:
            phone.delete()

        phones = Phone.objects.filter(member=request.user)

    return render(request, "list_contacts.html", {"phones": phones})


@login_required
def register_address(request):
    """Registra um novo endereço para o usuário logado.

    Valida e salva o endereço associado ao usuário.
    """
    user: Member = request.user

    form = AddressForm(request.POST)
    address = None  # type: ignore
    if form.is_valid():
        with transaction.atomic():
            address: Address = form.save(commit=False)
            address.member = user  # type: ignore
            # MANUTENÇÃO: Remover user.save() se não há mudança direta no usuário
            address.save()
            messages.success(request, "Endereço cadastrado com sucesso!")

            form = AddressForm(instance=address)

    return render(
        request,
        "location.html",
        {
            "address_form": form,
            "address": address,
            "status_location": "create",
        },
    )


@login_required
def edit_address(request):
    """Atualiza o endereço do usuário logado.

    Recupera o endereço existente e permite edição via formulário.
    Se o usuário não tiver endereço, redireciona para a criação.
    """
    address = getattr(request.user, "address", None)

    if address is None:
        messages.info(request, "Nenhum endereço cadastrado para editar.")
        return render(
            request,
            "location.html",
            {"address_form": AddressForm(), "address": None},
        )

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
    """Deleta o endereço do usuário logado, se existir."""
    form = AddressForm()
    address = getattr(request.user, "address", None)

    if address is not None:
        with transaction.atomic():
            address.delete()
        messages.success(request, "Endereço deletado com sucesso!")
    else:
        messages.info(request, "Nenhum endereço cadastrado para deletar.")

    return render(request, "location.html", {"address_form": form, "address": None})


# def forgot_password(request):
#     """Inicia o processo de recuperação de senha.

#     Gera token de reset de senha se o email for encontrado e envia via email.
#     """
#     message = "Se o emeil foi encontrado, foi enviado a url de reset de senha"
#     email = request.POST.get("email_forgot")
#     with transaction.atomic():
#         member = get_object_or_404(Member, email=email)

#         if member:
#             access = ResetPasswordAccess.objects.filter(member=member).first()
#             if access:
#                 if access.expired_at:
#                     # MANUTENÇÃO: Remover print() em produção
#                     if timezone.make_aware(datetime.now()) > access.expired_at:
#                         access.delete()
#                     else:
#                         # MANUTENÇÃO: Usar logger.info() ou remover
#                         # MANUTENÇÃO: Usar configuração para URL ao invés de hardcoded localhost:8000
#                         send_mail(
#                             "Reset de senha",
#                             f"http://localhost:8000/accounts/reset_password/{access.token}",
#                             member.email,
#                             ["pedrohenriquedasilva204@gmail.com"],
#                         )  # type: ignore
#                         return render(
#                             request,
#                             "forgot_password.html",
#                             {"message": message},
#                         )

#             try:
#                 reset_password = ResetPasswordAccess()
#                 reset_password.member = member
#                 reset_password.save()
#                 # MANUTENÇÃO: Usar configuração para URL e destinatário de email
#                 send_mail(
#                     "Reset de senha",
#                     f"http://localhost:8000/accounts/reset_password/{reset_password.token}",
#                     member.email,
#                     ["pedrohenriquedasilva204@gmail.com"],
#                 )  # type: ignore
#             # MANUTENÇÃO: Especificar exceção em vez de Exception genérica
#             except Exception:
#                 ...

#     return render(request, "forgot_password.html", {"message": message})


# def reset_password(request, token):
#     """Processa o reset de senha usando token válido.

#     Valida o token, verifica expiração e atualiza a senha do usuário.
#     """
#     access = get_object_or_404(ResetPasswordAccess, token=token)

#     if access.expired_at:
#         if timezone.make_aware(datetime.now()) > access.expired_at:
#             messages.error(request, "Token expirado")
#             access.delete()

#             return redirect(reverse("login"))

#     if request.method == "POST":
#         password1 = request.POST.get("password")
#         password2 = request.POST.get("confirm_password")
#         # MANUTENÇÃO: Validar senhas (comprimento, força) antes de salvar
#         if password1 == password2:
#             member = access.member

#             member.set_password(password1)

#             member.save()

#             access.delete()

#             return redirect(reverse("login"))

#     return render(request, "reset_password.html", {"token": token})
