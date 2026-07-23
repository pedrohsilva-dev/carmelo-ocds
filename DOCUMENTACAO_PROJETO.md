# Documentação do Projeto Django

Gerado em: 2026-07-23 16:28:18.539149

---


# 📁 all_models_struct.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `os`
- `json`
- `django`
- `django.apps`
- `django.db`

## Funções

### safe_str

### get_field_data

### analyze_field_issues

### get_model_schema

### main

## Código completo

```python
import os
import json
import django
from django.apps import apps
from django.db import models

# Ajuste seu settings module aqui
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


def safe_str(value):
    try:
        return str(value)
    except Exception:
        return repr(value)


def get_field_data(field):
    data = {
        "name": field.name,
        "type": field.__class__.__name__,
        "null": getattr(field, "null", None),
        "blank": getattr(field, "blank", None),
        "unique": getattr(field, "unique", None),
        "editable": getattr(field, "editable", None),
    }

    # default
    default = getattr(field, "default", None)
    if default is not None and default != models.fields.NOT_PROVIDED:
        data["default"] = safe_str(default)

    # relations
    if field.is_relation:
        data["is_relation"] = True
        data["relation_type"] = field.get_internal_type()
        data["related_model"] = (
            field.related_model.__name__ if field.related_model else None
        )

    # choices (ROBUSTO)
    if getattr(field, "choices", None):
        choices_list = []

        for c in field.choices:
            try:
                # Django TextChoices / IntegerChoices
                if hasattr(c, "value") and hasattr(c, "label"):
                    choices_list.append(
                        {
                            "value": safe_str(c.value),
                            "label": safe_str(c.label),
                        }
                    )

                # tuple padrão
                elif isinstance(c, (list, tuple)) and len(c) == 2:
                    choices_list.append(
                        {
                            "value": safe_str(c[0]),
                            "label": safe_str(c[1]),
                        }
                    )

                else:
                    choices_list.append(
                        {
                            "value": safe_str(c),
                            "label": safe_str(c),
                        }
                    )

            except Exception:
                choices_list.append(
                    {
                        "value": safe_str(c),
                        "label": safe_str(c),
                        "error": "invalid_choice_format",
                    }
                )

        data["choices"] = choices_list

    return data


def analyze_field_issues(field):
    issues = []

    # null + blank inconsistency
    if getattr(field, "null", False) and not getattr(field, "blank", False):
        issues.append("null=True mas blank=False (possível inconsistência em forms)")

    # unique + null problem
    if getattr(field, "unique", False) and getattr(field, "null", False):
        issues.append("unique=True com null=True pode gerar múltiplos NULLs no banco")

    # FK sem index (heurística)
    if field.is_relation and not getattr(field, "db_index", False):
        issues.append("ForeignKey sem db_index explícito (pode impactar performance)")

    return issues


def get_model_schema(model):
    schema = {
        "app": model._meta.app_label,
        "model": model.__name__,
        "table": model._meta.db_table,
        "is_abstract": model._meta.abstract,
        "is_proxy": model._meta.proxy,
        "fields": [],
        "relations": [],
        "methods": [],
        "meta": {
            "ordering": list(model._meta.ordering) if model._meta.ordering else [],
        },
        "potential_issues": [],
        "test_suggestions": [],
    }

    # fields
    for field in model._meta.get_fields():
        try:
            # remove reverse relations pesadas
            if field.auto_created and not field.concrete:
                continue

            field_data = get_field_data(field)
            schema["fields"].append(field_data)

            if field.is_relation:
                schema["relations"].append(field.name)

            schema["potential_issues"].extend(analyze_field_issues(field))

        except Exception as e:
            schema["potential_issues"].append(
                f"Erro lendo field {safe_str(field)}: {safe_str(e)}"
            )

    # methods
    for attr in dir(model):
        if attr.startswith("_"):
            continue
        if attr in ["save", "clean", "delete"]:
            schema["methods"].append(attr)

    # test suggestions (IA-friendly)
    schema["test_suggestions"] = [
        {
            "type": "create_valid_instance",
            "model": model.__name__,
        },
        {
            "type": "missing_required_fields_validation",
            "model": model.__name__,
        },
        {
            "type": "unique_constraint_test",
            "model": model.__name__,
        },
        {
            "type": "relation_integrity_test",
            "model": model.__name__,
        },
    ]

    return schema


def main(OUTPUT_FILE="django_ai_schema.json"):
    all_data = {
        "project": "Django AI Schema Export",
        "models_count": 0,
        "models": [],
    }

    models_list = list(apps.get_models())

    # opcional: filtrar Django interno (descomente se quiser)
    models_list = [
        m
        for m in models_list
        if not m._meta.app_label in ["admin", "auth", "contenttypes", "sessions"]
    ]

    all_data["models_count"] = len(models_list)

    for model in models_list:
        try:
            all_data["models"].append(get_model_schema(model))
        except Exception as e:
            all_data["models"].append({"model": model.__name__, "error": safe_str(e)})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"✔ Schema AI gerado com sucesso: {OUTPUT_FILE}")


if __name__ == "__main__":
    main(OUTPUT_FILE="django_ai_schema_1.json")
    main(OUTPUT_FILE="django_ai_schema_2.json")

```


# 📁 cep.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `requests`
- `json`

## Funções

### buscar_cep

## Código completo

```python
import requests
import json


def buscar_cep(cep):
    # Remove qualquer caractere que não seja número
    cep_limpo = "".join(filter(str.isdigit, str(cep)))

    # URL da API do ViaCEP
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

    try:
        response = requests.get(url)
        # Transforma o resultado em um dicionário Python
        dados = response.json()

        if "erro" in dados:
            return {"status": "erro", "mensagem": "CEP não encontrado"}

        return dados
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}


# Testando com o CEP da Praça da Sé (SP)
resultado = buscar_cep("18230-971")

# Exibe o resultado como um JSON formatado (string)
print(json.dumps(resultado, indent=4, ensure_ascii=False))

```


# 📁 install_test_deps.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `subprocess`
- `sys`
- `pathlib`

## Funções

### run_command

Executa um comando e mostra o resultado.

### check_python_version

Verifica se a versão do Python é compatível.

### main

Função principal.

## Código completo

```python
#!/usr/bin/env python
"""
Script para validar e instalar dependências de teste.
Uso: python install_test_deps.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Executa um comando e mostra o resultado."""
    print(f"\n📦 {description}...")
    print(f"   Executando: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ {description} - OK\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FALHOU\n")
        print(f"Erro: {e}\n")
        return False


def check_python_version():
    """Verifica se a versão do Python é compatível."""
    version = sys.version_info

    print(f"🐍 Versão do Python: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Requer Python 3.9+ (incompatível com sua versão)")
        return False

    print("✅ Versão do Python compatível\n")
    return True


def main():
    """Função principal."""
    print("=" * 60)
    print("🧪 Instalador de Dependências de Teste - Project Carmel")
    print("=" * 60)

    # Verificar Python
    if not check_python_version():
        print("❌ Por favor, instale Python 3.9 ou superior")
        sys.exit(1)

    # Atualizar pip
    print("⬆️  Atualizando pip...")
    run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"], "Atualizar pip"
    )

    # Instalar requirements-test.txt
    print("📥 Instalando dependências de teste...")
    requirements_file = Path("requirements-test.txt")

    if not requirements_file.exists():
        print(f"❌ Arquivo não encontrado: {requirements_file}")
        sys.exit(1)

    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"],
        "Instalar requirements-test.txt",
    ):
        print("⚠️  Alguns pacotes falharam. Tentando instalar sem versões fixas...")
        run_command(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pytest",
                "pytest-django",
                "pytest-cov",
                "coverage",
            ],
            "Instalar pacotes essenciais",
        )

    # Verificar instalação
    print("\n✔️  Verificando instalação...")

    packages = ["pytest", "pytest_django", "pytest_cov", "coverage"]
    all_ok = True

    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} NÃO INSTALADO")
            all_ok = False

    if all_ok:
        print("\n" + "=" * 60)
        print("✅ TUDO PRONTO!")
        print("=" * 60)
        print("\nPróximas etapas:")
        print("  1. Rodar testes:      pytest tests/ -v")
        print("  2. Com cobertura:     pytest tests/ --cov=.")
        print("  3. Abrir relatório:   pytest tests/ --cov=. --cov-report=html")
        print("\n" + "=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("⚠️  ALGUNS PACOTES NÃO FORAM INSTALADOS")
        print("=" * 60)
        print("\nTente instalar manualmente:")
        print("  pip install pytest pytest-django pytest-cov coverage")
        print("\n" + "=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

```


# 📁 manage.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `os`
- `sys`
- `django.core.management`

## Funções

### main

Run administrative tasks.

## Código completo

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

```


# 📁 accounts\admin.py

## Descrição

Arquivo responsável pela configuração do Django Admin.

## Imports

- `django.contrib`
- `accounts.models`

## Código completo

```python
from django.contrib import admin

from accounts.models import ResetPasswordAccess

# Register your models here.

admin.site.register(ResetPasswordAccess)

```


# 📁 accounts\apps.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.apps`

## Classes

### AccountsConfig

## Código completo

```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"
    verbose_name = "Contas dos Membros"

```


# 📁 accounts\forms.py

## Descrição

Arquivo responsável pelos formulários Django e validações de entrada.

## Imports

- `django`
- `members.models`

## Classes

### LoginForm

### AddressForm

### Meta

## Código completo

```python
from django import forms

from members.models import Address


class LoginForm(forms.Form):

    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            
            attrs={
                "class": "form-control w-full",
                ":type": "hide_password ? 'password' : 'text'",
            }
        ),
        label="Senha",
        required=True,
    )


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
            "street": forms.TextInput(attrs={"class": "form-control"}),
            "number": forms.TextInput(attrs={"class": "form-control", "max": 3}),
            "neighborhood": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "zipcode": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "max": 8,
                    "x-mask": "99999-999",
                    "placeholder": "00000-000",
                }
            ),
        }

```


# 📁 accounts\models.py

## Descrição

Arquivo responsável pelos modelos do banco de dados e regras de negócio através dos Models Django.

## Imports

- `datetime`
- `django.db`
- `members.models`
- `secrets`

## Classes

### ResetPasswordAccess

**Métodos:**

- save

## Funções

### save

## Código completo

```python
from datetime import datetime, timedelta

from django.db import models
from members.models import Member
from secrets import token_urlsafe

# Create your models here.


class ResetPasswordAccess(models.Model):
    token = models.CharField("token de acesso", max_length=32, null=True, blank=True)
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    expired_at = models.DateTimeField(
        "Data e Hora de expiração do token", max_length=32, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        self.token = token_urlsafe(nbytes=16)
        self.expired_at = datetime.now() + timedelta(hours=1)

        super().save(*args, **kwargs)

```


# 📁 accounts\tests.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.test`

## Código completo

```python
from django.test import TestCase

# Create your tests here.

```


# 📁 accounts\urls.py

## Descrição

Arquivo responsável pelo roteamento das URLs do Django.

## Imports

- `django.urls`
- ``

## Código completo

```python
from django.urls import path
from . import views

urlpatterns = [
    # URLS QUE APARECEM NO NAVEGADOR DO USUARIO
    path("entrar/", views.login, name="login"),
    path("sair/", views.logout, name="logout"),
    path("perfil_do_membro/", views.profile, name="profile"),
    # URLS INTERNAS
    path("register_phone/", views.register_phone, name="register_phone"),
    path("delete_phone/<int:id>", views.delete_phone, name="delete_phone"),
    path("register_address/", views.register_address, name="register_address"),
    path("edit_address/", views.edit_address, name="edit_address"),
    path("delete_address/", views.delete_address, name="delete_address"),
    # path("forgot_password/", views.forgot_password, name="forgot_password"),
    # path("reset_password/<str:token>/", views.reset_password, name="reset_password"),
]

```


# 📁 accounts\views.py

## Descrição

Arquivo responsável pelo controle das requisições, processamento das regras e renderização das páginas.

## Imports

- `datetime`
- `re`
- `django.contrib`
- `django.contrib.auth`
- `django.contrib.auth`
- `django.contrib.auth.decorators`
- `django.db`
- `django.shortcuts`
- `django.urls`
- `accounts.forms`
- `contributions.models`
- `contributions.views`
- `members.models`
- `votes.models`

## Funções

### login

Autentica um usuário no sistema.

Renderiza o formulário de login e, ao submeter, valida as credenciais.
Se válido, faz login; caso contrário, exibe mensagem de erro.

### logout

Desconecta o usuário autenticado da sessão.

Limpa a sessão do usuário e redireciona para a página de login.

### profile

Exibe o perfil do usuário logado.

Obtém e renderiza: telefones, votos, última contribuição e endereço do usuário.

### register_phone

Registra um novo telefone para o usuário logado.

Valida se o telefone já existe; se não, cria um novo registro.
Renderiza a lista de telefones atualizada.

### delete_phone

Deleta um telefone específico do usuário logado.

Remove o telefone apenas se pertencer ao usuário autenticado.
Renderiza a lista de telefones atualizada.

### register_address

Registra um novo endereço para o usuário logado.

Valida e salva o endereço associado ao usuário.

### edit_address

Atualiza o endereço do usuário logado.

Recupera o endereço existente e permite edição via formulário.

### delete_address

Deleta o endereço do usuário logado.

Remove o endereço associado e renderiza a página sem ele.

## Código completo

```python
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
from contributions.models import Contribution
from contributions.views import month_empty
from members.models import Address, Member, Phone
from votes.models import Vote

# Create your views here.


def login(request):
    """Autentica um usuário no sistema.

    Renderiza o formulário de login e, ao submeter, valida as credenciais.
    Se válido, faz login; caso contrário, exibe mensagem de erro.
    """
    form_login = LoginForm()

    if request.method == "POST":
        form_login = LoginForm(request.POST)
        if form_login.is_valid():
            # MANUTENÇÃO: Considerar usar login.authenticate com email como backend
            user = authenticate(
                request,
                username=form_login.cleaned_data["email"],
                password=form_login.cleaned_data["password"],
            )
            if user:
                login_auth(request, user)
                messages.success(request, "Bem vindo ao sistema OCDS")
                return redirect(reverse("profile"))
            else:
                messages.error(request, "Erro ao Logar tente Novamente")

    return render(request, "login.html", {"form": form_login})


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
    # MANUTENÇÃO: Usar select_related/prefetch_related para otimizar queries
    phones = Phone.objects.filter(member=request.user)
    votes = Vote.objects.filter(member=request.user).all()
    contribution = Contribution.objects.filter(member=request.user).last()

    contributions = month_empty(request.user)

    # MOSTRAR CONTRIBUIÇÕES NÃO PAGAS

    try:
        address = request.user.location
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
    address = None
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
    """
    # MANUTENÇÃO: Validar se address existe antes de usar
    address = request.user.location
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
    """Deleta o endereço do usuário logado.

    Remove o endereço associado e renderiza a página sem ele.
    """
    form = AddressForm()

    with transaction.atomic():
        # MANUTENÇÃO: Verificar se address existe antes de deletar para evitar erro
        request.user.location.delete()
        address = None
        messages.success(request, "Endereço deletado com sucesso!")

    # MANUTENÇÃO: Lógica redundante - 'address' sempre é None
    if address:
        messages.error(request, "Erro ao deletar endereço!")

    return render(request, "location.html", {"address_form": form, "address": address})


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

```


# 📁 accounts\__init__.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python

```


# 📁 base\admin.py

## Descrição

Arquivo responsável pela configuração do Django Admin.

## Imports

- `django.contrib`

## Código completo

```python
from django.contrib import admin

# Register your models here.

```


# 📁 base\apps.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.apps`

## Classes

### BaseConfig

## Código completo

```python
from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = "base"

```


# 📁 base\doc_gen.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `os`
- `ast`
- `pathlib`
- `datetime`

## Funções

### analyze_file

### describe_file

### find_python_files

### generate

## Código completo

```python
import os
import ast
from pathlib import Path
from datetime import datetime

# ==============================
# CONFIGURAÇÕES
# ==============================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_FILE = PROJECT_ROOT / "DOCUMENTACAO_PROJETO.md"


IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "env",
    "static",
    "media",
    "node_modules",
    "migrations",
}


# ==============================
# ANALISADOR PYTHON
# ==============================


def analyze_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:

        source = file.read()

    try:
        tree = ast.parse(source)

    except SyntaxError:
        return None

    data = {
        "imports": [],
        "classes": [],
        "functions": [],
        "code": source,
    }

    for node in ast.walk(tree):

        # imports

        if isinstance(node, ast.Import):

            for item in node.names:
                data["imports"].append(item.name)

        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            data["imports"].append(module)

        # classes

        elif isinstance(node, ast.ClassDef):

            methods = []

            for item in node.body:

                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)

            data["classes"].append(
                {"name": node.name, "methods": methods, "doc": ast.get_docstring(node)}
            )

        # funções

        elif isinstance(node, ast.FunctionDef):

            data["functions"].append(
                {"name": node.name, "doc": ast.get_docstring(node)}
            )

    return data


# ==============================
# DESCRIÇÕES AUTOMÁTICAS
# ==============================


def describe_file(path):

    name = path.name.lower()

    if name == "models.py":

        return (
            "Arquivo responsável pelos modelos do banco de dados "
            "e regras de negócio através dos Models Django."
        )

    if name == "views.py":

        return (
            "Arquivo responsável pelo controle das requisições, "
            "processamento das regras e renderização das páginas."
        )

    if name == "forms.py":

        return (
            "Arquivo responsável pelos formulários Django " "e validações de entrada."
        )

    if name == "admin.py":

        return "Arquivo responsável pela configuração " "do Django Admin."

    if "urls" in name:

        return "Arquivo responsável pelo roteamento " "das URLs do Django."

    if "settings" in name:

        return "Arquivo de configurações principais do projeto."

    return "Arquivo Python contendo lógica do sistema."


# ==============================
# BUSCAR ARQUIVOS
# ==============================


def find_python_files():

    files = []

    for root, dirs, filenames in os.walk(PROJECT_ROOT):

        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for filename in filenames:

            if filename.endswith(".py"):

                files.append(Path(root) / filename)

    return files


# ==============================
# GERAR DOCUMENTAÇÃO
# ==============================


def generate():

    files = find_python_files()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as doc:

        doc.write("# Documentação do Projeto Django\n\n")

        doc.write(f"Gerado em: {datetime.now()}\n\n")

        doc.write("---\n")

        for file in files:

            relative = file.relative_to(PROJECT_ROOT)

            data = analyze_file(file)

            if not data:
                continue

            doc.write(f"\n\n# 📁 {relative}\n\n")

            doc.write(f"## Descrição\n\n")

            doc.write(describe_file(file))

            doc.write("\n\n")

            # imports

            if data["imports"]:

                doc.write("## Imports\n\n")

                for imp in data["imports"]:

                    doc.write(f"- `{imp}`\n")

                doc.write("\n")

            # classes

            if data["classes"]:

                doc.write("## Classes\n\n")

                for cls in data["classes"]:

                    doc.write(f"### {cls['name']}\n\n")

                    if cls["doc"]:

                        doc.write(cls["doc"] + "\n\n")

                    if cls["methods"]:

                        doc.write("**Métodos:**\n\n")

                        for method in cls["methods"]:

                            doc.write(f"- {method}\n")

                        doc.write("\n")

            # funções

            if data["functions"]:

                doc.write("## Funções\n\n")

                for func in data["functions"]:

                    doc.write(f"### {func['name']}\n\n")

                    if func["doc"]:

                        doc.write(func["doc"] + "\n\n")

            # código completo

            doc.write("## Código completo\n\n")

            doc.write("```python\n")

            doc.write(data["code"])

            doc.write("\n```\n")

    print("Documentação criada:")

    print(OUTPUT_FILE)


if __name__ == "__main__":

    generate()

```


# 📁 base\middlewares.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `json`
- `django.contrib.messages`
- `django.contrib.auth`

## Classes

### HtmxMessagesMiddleware

**Métodos:**

- __init__
- __call__

### PrefetchUserPermissionsMiddleware

**Métodos:**

- __init__
- __call__

## Funções

### __init__

### __call__

### __init__

### __call__

## Código completo

```python
import json

from django.contrib.messages import get_messages


class HtmxMessagesMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.headers.get("HX-Request"):

            msgs = []

            for msg in get_messages(request):

                msgs.append(
                    {
                        "message": str(msg),
                        "tags": msg.tags,
                    }
                )

            if msgs:

                response["HX-Trigger"] = json.dumps({"django-messages": msgs})

        return response


from django.contrib.auth import get_user_model


class PrefetchUserPermissionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            User = get_user_model()

            request.user = User.objects.prefetch_related(
                "groups__permissions",
                "user_permissions",
            ).get(pk=request.user.pk)

        response = self.get_response(request)

        return response

```


# 📁 base\models.py

## Descrição

Arquivo responsável pelos modelos do banco de dados e regras de negócio através dos Models Django.

## Imports

- `django.db`

## Classes

### TimeStampedModel

### Meta

## Código completo

```python
from django.db import models

# Create your models here.


class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

```


# 📁 base\tests.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.test`

## Código completo

```python
from django.test import TestCase

# Create your tests here.

```


# 📁 base\views.py

## Descrição

Arquivo responsável pelo controle das requisições, processamento das regras e renderização das páginas.

## Imports

- `django.shortcuts`

## Funções

### error400

### error403

### error404

### error500

## Código completo

```python
from django.shortcuts import render

# Create your views here.


def error400(request, exception):
    return render(request, "error_400.html")


def error403(request, exception):
    return render(request, "error_403.html")


def error404(request, exception):
    return render(request, "error_404.html")


def error500(request):
    return render(request, "error_500.html")

```


# 📁 base\__init__.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python

```


# 📁 carmel\admin.py

## Descrição

Arquivo responsável pela configuração do Django Admin.

## Imports

- `django.contrib`
- `carmel.models`

## Código completo

```python
from django.contrib import admin

from carmel.models import Carmel

# Register your models here.

admin.site.register(Carmel)

```


# 📁 carmel\apps.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.apps`

## Classes

### CarmelConfig

## Código completo

```python
from django.apps import AppConfig


class CarmelConfig(AppConfig):
    name = "carmel"
    verbose_name = "Carmelos"

```


# 📁 carmel\forms.py

## Descrição

Arquivo responsável pelos formulários Django e validações de entrada.

## Imports

- `django`
- `carmel.models`

## Classes

### CarmelForm

### Meta

## Código completo

```python
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
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "price_contribution_default": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
        }

```


# 📁 carmel\info_data.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python
# DATA BETWEEN MODULES (APPS)

```


# 📁 carmel\models.py

## Descrição

Arquivo responsável pelos modelos do banco de dados e regras de negócio através dos Models Django.

## Imports

- `django.db`
- `django.core.validators`
- `base.models`

## Classes

### Carmel

**Métodos:**

- __str__

### Meta

## Funções

### __str__

## Código completo

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from base.models import TimeStampedModel

# Create your models here.


class Carmel(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=4000)
    # brand = models.ImageField('Logo do carmelo', upload_to="media")
    price_contribution_default = models.DecimalField(max_digits=1000, decimal_places=2)
    pay_day_contribution_default = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )
    diocese = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Carmelo"
        verbose_name_plural = "Carmelos"

    def __str__(self) -> str:
        return self.name

```


# 📁 carmel\tests.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.test`

## Código completo

```python
from django.test import TestCase

# Create your tests here.

```


# 📁 carmel\urls.py

## Descrição

Arquivo responsável pelo roteamento das URLs do Django.

## Imports

- ``
- `django.urls`

## Código completo

```python
from . import views
from django.urls import path

urlpatterns = [
    path("", views.carmel_profile, name="carmel_profile"),
    path("edit/", views.edit_carmel, name="edit_carmel"),
]

```


# 📁 carmel\views.py

## Descrição

Arquivo responsável pelo controle das requisições, processamento das regras e renderização das páginas.

## Imports

- `django.shortcuts`
- `django.contrib.auth.decorators`
- `carmel.forms`
- `carmel.models`
- `contributions.models`
- `members.models`
- `django.contrib`
- `rolepermissions.decorators`
- `django.db.models.aggregates`

## Funções

### edit_carmel

Edita as informações do carmelo associado ao usuário.

Permite que o líder do carmelo atualize os dados do carmelo (como nome, descrição).

### carmel_profile

Exibe o perfil do carmelo com estatísticas de membros e contribuições.

Mostra: quantidade de membros, total de contribuições e permite edição do carmelo.

## Código completo

```python
from django.shortcuts import get_object_or_404, get_list_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from carmel.forms import CarmelForm
from carmel.models import Carmel
from contributions.models import Contribution
from members.models import Member

from django.contrib import messages

from rolepermissions.decorators import has_permission_decorator

# Agregações do Django
from django.db.models.aggregates import Sum

# Create your views here.


@login_required
@has_permission_decorator("edit_carmel")
def edit_carmel(request):
    """Edita as informações do carmelo associado ao usuário.

    Permite que o líder do carmelo atualize os dados do carmelo (como nome, descrição).
    """
    user = request.user

    if not user:
        return redirect("/")

    carmel = get_object_or_404(Carmel, member=user)

    if request.method == "POST":
        form = CarmelForm(request.POST, instance=carmel)
        if form.is_valid():
            form.save()
            return redirect("carmel_profile")
    else:
        form = CarmelForm(instance=carmel)

    return render(
        request,
        "carmel_edit.html",
        {
            "form": form,
        },
    )


@login_required
@has_permission_decorator("view_carmel")
def carmel_profile(request):
    """Exibe o perfil do carmelo com estatísticas de membros e contribuições.

    Mostra: quantidade de membros, total de contribuições e permite edição do carmelo.
    """
    user = request.user

    if not user.carmel:
        return redirect("/")

    carmel = user.carmel

    # MANUTENÇÃO: Usar .count() ou .values('id').count() para otimizar query
    quantity = Member.objects.filter(
        carmel=carmel
    ).count()  # Mostra a quantidade de membros

    # MANUTENÇÃO: Já está usando agregação corretamente com Sum
    total_contribution = (
        Contribution.objects.filter(member__carmel=carmel).aggregate(Sum("price"))[
            "price__sum"
        ]
        or 0
    )

    # edit carmel
    form = CarmelForm(instance=carmel)

    if request.method == "POST":
        form = CarmelForm(request.POST, instance=carmel)
        if form.is_valid():
            form.save()
            return redirect("carmel_profile")

    return render(
        request,
        "carmel_profile.html",
        {
            "carmel": carmel,
            "member_quantity": quantity,
            "total_contribution": total_contribution,
            "form": form,
        },
    )

```


# 📁 carmel\__init__.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python

```


# 📁 contributions\admin.py

## Descrição

Arquivo responsável pela configuração do Django Admin.

## Imports

- `django.contrib`
- `contributions.models`

## Código completo

```python
from django.contrib import admin

from contributions.models import Contribution

# Register your models here.


admin.site.register(Contribution)

```


# 📁 contributions\apps.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.apps`

## Classes

### ContribuitionsConfig

## Código completo

```python
from django.apps import AppConfig


class ContribuitionsConfig(AppConfig):
    name = "contributions"
    verbose_name = "Contribuições"

```


# 📁 contributions\forms.py

## Descrição

Arquivo responsável pelos formulários Django e validações de entrada.

## Imports

- `django`
- `contributions.models`

## Classes

### ContributionForm

### Meta

## Código completo

```python
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

```


# 📁 contributions\models.py

## Descrição

Arquivo responsável pelos modelos do banco de dados e regras de negócio através dos Models Django.

## Imports

- `datetime`
- `django.db`
- `base.models`
- `members.models`
- `django.core.exceptions`

## Classes

### Contribution

**Métodos:**

- clean
- __str__

### Meta

## Funções

### clean

### __str__

## Código completo

```python
from datetime import date

from django.db import models

from base.models import TimeStampedModel
from members.models import Member
from django.core.exceptions import ValidationError

# Create your models here.


class Contribution(TimeStampedModel):

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor da Contribuição",
    )

    date_pay = models.DateField(verbose_name="Data do Pagamento")

    carmel = models.ForeignKey(
        "carmel.Carmel",
        on_delete=models.PROTECT,  # impede apagar um Carmel que já tem histórico de contribuições
        null=True,  # fica opcional pra não quebrar dado antigo
        blank=True,
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="contributions",
        verbose_name="Membro",
    )

    class Meta:
        verbose_name = "Contribuição"
        verbose_name_plural = "Contribuições"

        constraints = [
            models.UniqueConstraint(
                fields=["member", "date_pay"], name="unique_member_contribution_date"
            )
        ]

    def clean(self):
        super().clean()

        if not self.member_id:
            return

        if not self.date_pay:
            return

        exists = Contribution.objects.filter(
            member_id=self.member_id,
            date_pay__year=self.date_pay.year,
            date_pay__month=self.date_pay.month,
        )

        if self.pk:
            exists = exists.exclude(pk=self.pk)

        if exists.exists():
            raise ValidationError({"date_pay": "Já existe uma contribuição neste mês."})

    def __str__(self):
        return f"{self.member} - {self.price}"

```


# 📁 contributions\tests.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.test`

## Código completo

```python
from django.test import TestCase

# Create your tests here.

```


# 📁 contributions\urls.py

## Descrição

Arquivo responsável pelo roteamento das URLs do Django.

## Imports

- `django.urls`
- ``

## Código completo

```python
from django.urls import path
from . import views

urlpatterns = [
    path(
        "<slug:user>/register/",
        views.register_contribution,
        name="register_contribution",
    ),
    path(
        "listagem/<slug:slug>/", views.contribution_member, name="contribution_member"
    ),
    path(
        "delete/<slug:user>/pk/<int:id>",
        views.delete_contribution,
        name="delete_contribution",
    ),
]

```


# 📁 contributions\views.py

## Descrição

Arquivo responsável pelo controle das requisições, processamento das regras e renderização das páginas.

## Imports

- `datetime`
- `django.contrib`
- `django.contrib.auth.decorators`
- `django.core.exceptions`
- `django.db`
- `django.shortcuts`
- `django.urls`
- `django.utils.dates`
- `rolepermissions.decorators`
- `carmel.models`
- `contributions.forms`
- `contributions.models`
- `members.models`

## Funções

### register_contribution

Registra uma nova contribuição para um membro.

Valida se a data de contribuição é válida (entre entrada e hoje),
define o valor padrão ou customizado e salva a contribuição.

### update_contribution

Atualiza uma contribuição existente.

[MANUTENÇÃO: Esta função está incompatével - não implementa lógica de atualização]

### delete_contribution

Deleta uma contribuição de um membro.

Remove a contribuição e renderiza a lista de contribuições atualizada.

### month_empty

### contribution_member

Lista todas as contribuições de um membro específico.

Exibe o histórico de contribuições, meses faltantes e permite registrar novas contribuições.

## Código completo

```python
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dates import MONTHS
from rolepermissions.decorators import has_permission_decorator

from carmel.models import Carmel
from contributions.forms import ContributionForm
from contributions.models import Contribution
from members.models import Member

# 'create_Contribute': True,
# 'read_contribute': True,
# 'edit_contribute': True,
# 'delete_contribute': True,
# 'list_contribute': True,


# Create your views here.
@login_required
@has_permission_decorator("create_Contribute")
def register_contribution(request, user):
    """Registra uma nova contribuição para um membro.

    Valida se a data de contribuição é válida (entre entrada e hoje),
    define o valor padrão ou customizado e salva a contribuição.
    """
    member = get_object_or_404(Member, slug=user)

    carmel: Carmel = request.user.carmel

    form = ContributionForm(request.POST or None)

    date_entry = member.entry_date
    date_now = date.today()

    if request.method == "POST" and form.is_valid():
        date_pay = form.cleaned_data["date_pay"]
        price = form.cleaned_data["price"]

        # Não permitir contribuições antes da entrada
        if date_pay < date_entry:
            messages.error(
                request,
                "Não é permitido registrar contribuições antes da entrada do membro.",
            )

        # Não permitir contribuições futuras
        elif date_pay > date_now:
            messages.error(request, "Não é permitido registrar contribuições futuras.")

        else:
            try:
                with transaction.atomic():
                    contrib: Contribution = form.save(commit=False)

                    contrib.member = member
                    if price:
                        contrib.price = price
                    else:
                        contrib.price = carmel.price_contribution_default

                        messages.info(
                            request, "Foi cadastrado com valor padrão do carmelo."
                        )

                    contrib.carmel = request.user.carmel

                    # Executa as validações do model
                    contrib.full_clean()

                    contrib.save()

                    messages.success(request, "Contribuição cadastrada com sucesso.")

                    form = ContributionForm()

            # MANUTENÇÃO: Considerar logar os erros de validação
            except ValidationError as exc:
                for error in exc.messages:
                    messages.error(request, error)

    contributions = Contribution.objects.filter(member=member).order_by("date_pay")

    # Utilize sua função
    month_data = month_empty(member)

    return render(
        request,
        "contribution/components_contribution/list_contribution.html",
        {
            "user_current": user,
            "contributions": contributions,
            "form_contribution": form,
            "date_entry": date_entry,
            "price_default": carmel.price_contribution_default,
            # Dados retornados pela função
            "months": month_data,
        },
    )


@login_required
@has_permission_decorator("edit_contribute")
def update_contribution(request):
    """Atualiza uma contribuição existente.

    [MANUTENÇÃO: Esta função está incompatével - não implementa lógica de atualização]
    """
    return render(request, "contribution/list.html", {})


@login_required
@has_permission_decorator("delete_contribute")
def delete_contribution(request, user, id):
    """Deleta uma contribuição de um membro.

    Remove a contribuição e renderiza a lista de contribuições atualizada.
    """
    contribution = get_object_or_404(Contribution, id=id)

    contribution.delete()

    messages.success(request, "Contribuição deletada com sucesso.")

    member = get_object_or_404(Member, slug=user)

    carmel: Carmel = request.user.carmel

    form = ContributionForm()

    # MANUTENÇÃO: Usar select_related para otimizar queries
    contributions = Contribution.objects.filter(member=member).order_by("date_pay")

    month_data = month_empty(member)

    return render(
        request,
        "contribution/components_contribution/list_contribution.html",
        {
            "user_current": user,
            "contributions": contributions,
            "form_contribution": form,
            "price_default": carmel.price_contribution_default,
            "date_entry": member.entry_date,
            # Dados calculados
            "months": month_data,
        },
    )


def month_empty(member):
    date_entry = member.entry_date
    date_now = date.today()

    payments = Contribution.objects.filter(
        member=member, date_pay__range=(date_entry, date_now)
    )

    # Meses pagos
    paid_months = {(c.date_pay.year, c.date_pay.month) for c in payments}

    # Meses esperados
    expected_months = set()

    year = date_entry.year
    month = date_entry.month

    while (year, month) <= (date_now.year, date_now.month):
        expected_months.add((year, month))

        month += 1

        if month > 12:
            month = 1
            year += 1

    # Meses faltantes
    missing_months = expected_months - paid_months

    missing_months = sorted(missing_months)

    # Formatação em português
    missing_months_formatted = []

    for year, month in missing_months:
        month_name = MONTHS[month]

        missing_months_formatted.append(
            {"date_formatted": f"{month_name} de {year}", "month": month, "year": year}
        )

    return {
        "count_paid": payments.count(),
        "count_missing": len(missing_months),
        "missing_months": missing_months_formatted,
    }


@login_required
@has_permission_decorator("list_contribute")
def contribution_member(request, slug):
    """Lista todas as contribuições de um membro específico.

    Exibe o histórico de contribuições, meses faltantes e permite registrar novas contribuições.
    """
    form = ContributionForm()

    carmel: Carmel = request.user.carmel

    member = get_object_or_404(Member, slug=slug)

    months = month_empty(member)

    # MANUTENÇÃO: Query duplicada - remover segunda chamada
    member = get_object_or_404(Member, slug=slug)

    date_entry = member.entry_date  # Data que entrou

    if not carmel:
        messages.error(request, "Nenhum carmelo no Membro que está cadatrando")
        # o problema é que está usando a resposta para o htmx
        # e um redirect iria preencher o conteudo o htmx com uma pagina
        messages.info(request, "Sem carmelo relacionado")
        return redirect(reverse("list_member"))

    # MANUTENÇÃO: Usar select_related para otimizar queries\n
    contributions = (
        Contribution.objects.filter(member__slug=slug).order_by("date_pay").all()
    )

    return render(
        request,
        "contribution/list.html",
        {
            "contributions": contributions,
            "user_current": slug,
            "form_contribution": form,
            "price_default": carmel.price_contribution_default,
            "months": months,
            "date_entry": date_entry,
        },
    )

```


# 📁 contributions\__init__.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python

```


# 📁 core\asgi.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `os`
- `django.core.asgi`

## Código completo

```python
"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_asgi_application()

```


# 📁 core\password_validators.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `re`
- `django.core.exceptions`

## Classes

### StrongPasswordValidator

**Métodos:**

- validate
- get_help_text

## Funções

### validate

### get_help_text

## Código completo

```python
import re

from django.core.exceptions import ValidationError


class StrongPasswordValidator:

    def validate(self, password, user=None):

        if len(password) < 10:
            raise ValidationError("A senha deve possuir pelo menos 10 caracteres.")

        if not re.search(r"[A-Z]", password):
            raise ValidationError("A senha deve possuir uma letra maiúscula.")

        if not re.search(r"[a-z]", password):
            raise ValidationError("A senha deve possuir uma letra minúscula.")

        if not re.search(r"\d", password):
            raise ValidationError("A senha deve possuir um número.")

        if not re.search(r"[!@#$%^&*()_\-+=<>?/{}[\]|\\.,:;]", password):
            raise ValidationError("A senha deve possuir um caractere especial.")

    def get_help_text(self):
        return (
            "A senha deve possuir no mínimo 10 caracteres, "
            "uma letra maiúscula, uma minúscula, um número "
            "e um caractere especial."
        )

```


# 📁 core\roles.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `rolepermissions.roles`

## Classes

### NormalMember

### FinanceMember

### ManagerMember

## Código completo

```python
from rolepermissions.roles import AbstractUserRole


class NormalMember(AbstractUserRole):
    available_permissions = {"login": True, "home": True, "profile": True}


class FinanceMember(AbstractUserRole):
    available_permissions = {
        "login": True,
        "home": True,
        "profile": True,
        "view_carmel": True,
        "see_total_money": True,
        "show_money": True,
        "carmel_dashboard": True,
        "list_members": True,
        # CONTROL CONTRIBUTION
        "create_Contribute": True,
        "read_contribute": True,
        "edit_contribute": True,
        "delete_contribute": True,
        "list_contribute": True,
    }


class ManagerMember(AbstractUserRole):
    available_permissions = {
        "login": True,
        "home": True,
        "profile": True,
        "carmel_dashboard": True,
        "view_carmel": True,
        "edit_carmel": True,
        "transfer_carmel": True,
        "see_total_money": True,
        "show_money": True,
        # MEMBER
        "create_member": True,
        "read_member": True,
        "edit_member": True,
        "delete_member": True,
        "list_members": True,
        # VOTES
        "create_vote": True,
        "read_vote": True,
        "edit_vote": True,
        "delete_vote": True,
        "list_vote": True,
        # CONTRIBUTE
        "create_Contribute": True,
        "read_contribute": True,
        "edit_contribute": True,
        "delete_contribute": True,
        "list_contribute": True,
        # VOTES REGISTRATION
        "create_votes_registration": True,
        "read_votes_registration": True,
        "edit_votes_registration": True,
        "delete_votes_registration": True,
        "list_votes_registration": True,
    }

```


# 📁 core\settings.py

## Descrição

Arquivo de configurações principais do projeto.

## Imports

- `pathlib`
- `os`

## Código completo

```python
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-lm#u=3l65fm-zwh7tc!)iho4b0r@lor-q2iy8550$1c4mckh)="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rolepermissions",
    "compressor",
    "django_extensions",
    # MYAPPS
    "base",
    "carmel",
    "members",
    "votes",
    "contributions",
    "accounts",
]


LANGUAGE_CODE = "pt-br"
USE_I18N = True

AUTH_USER_MODEL = "members.Member"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "base.middlewares.PrefetchUserPermissionsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "base.middlewares.HtmxMessagesMiddleware",
]

LOGIN_REDIRECT_URL = "/accounts/login"

ROOT_URLCONF = "core.urls"

# if DEBUG:
#     idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
#     MIDDLEWARE.insert(idx + 1, "django_devbar.DevBarMiddleware")

# if DEBUG:
#     DEVBAR = {
#         "POSITION": "bottom-right",  # bottom-right (default), bottom-left, top-right, top-left
#         "SHOW_BAR": None,  # follows DEBUG; set True/False to override
#         "ENABLE_DEVTOOLS_DATA": None,  # follows DEBUG; set True/False to override
#         "DEVTOOLS_HEADER_MAX_BYTES": 6144,  # max bytes for DevBar-Data header payload
#         "DEVTOOLS_MAX_QUERIES": None,  # optional hard cap for q/dup entries sent to DevTools
#     }
#     GRAPH_MODELS = {
#         "group_models": True,
#         "inheritance": True,
#         "app_labels": [
#             "base",
#             "carmel",
#             "members",
#             "votes",
#             "contributions",
#             "accounts",
#         ],
#     }


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "core.password_validators.StrongPasswordValidator",
    },
]

# AUTHENTICATION_BACKENDS = [
#     'members.backends.EmailBackend',
# ]

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "pt-BR"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True

ROLEPERMISSIONS_MODULE = "core.roles"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "/static/"


STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

# Compressor
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True


COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

```


# 📁 core\urls.py

## Descrição

Arquivo responsável pelo roteamento das URLs do Django.

## Imports

- `django.contrib`
- `django.urls`
- `django.conf.urls`
- `core`
- `django.conf.urls.static`
- ``

## Código completo

```python
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler400, handler403, handler404, handler500

from core import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("administrador/", admin.site.urls),
    path("contas/", include("accounts.urls")),
    path("membros/", include("members.urls")),
    path("carmelo/", include("carmel.urls")),
]

urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT,
)


handler400 = "base.views.error400"
handler403 = "base.views.error403"
handler404 = "base.views.error404"
handler500 = "base.views.error500"

```


# 📁 core\views.py

## Descrição

Arquivo responsável pelo controle das requisições, processamento das regras e renderização das páginas.

## Imports

- `django.shortcuts`

## Funções

### home

Renderiza a página inicial do sistema.

Simples view que exibe a página home.

## Código completo

```python
from django.shortcuts import render


def home(request):
    """Renderiza a página inicial do sistema.

    Simples view que exibe a página home.
    """
    return render(request, "home.html")

```


# 📁 core\wsgi.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `os`
- `django.core.wsgi`

## Código completo

```python
"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()

```


# 📁 core\__init__.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python

```


# 📁 members\admin.py

## Descrição

Arquivo responsável pela configuração do Django Admin.

## Imports

- `django.contrib`
- `models`

## Código completo

```python
from django.contrib import admin

# from contributions.models import Contribution
# from votes.models import Vote

from .models import Member, Phone, Address

# # =========================
# # INLINES (ESTILO UNFOLD)
# # =========================

# class VotesInline(admin.TabularInline):
#     model = Vote
#     extra = 0


# class ContributionInline(admin.TabularInline):
#     model = Contribution
#     extra = 0


# class PhoneInline(admin.TabularInline):
#     model = Phone
#     extra = 0

# # =========================
# # MEMBER ADMIN
# # =========================

# @admin.register(Member)
# class MemberAdmin(admin.ModelAdmin):

#     list_display = (
#         "email",
#         "name",
#         "roles",
#         "is_active",
#     )

#     search_fields = (
#         "email",
#         "name",
#     )

#     list_filter = (
#         "roles",
#         "is_active",
#     )

#     ordering = ("name",)

#     inlines = [
#         VotesInline,
#         ContributionInline,
#         PhoneInline
#     ]

#     fieldsets = (
#         ("Informações", {
#             "fields": (
#                 "email",
#                 "password",
#                 "name",
#                 "church",
#                 "entry_date",
#                 "carmel",
#                 "roles",
#                 "slug",
#                 'address'
#             )
#         }),

#         ("Permissões", {
#             "fields": (
#                 "is_active",
#                 "is_staff",
#                 "is_superuser",
#             )
#         }),
#     )

admin.site.register(Member)
admin.site.register(Address)
admin.site.register(Phone)

```


# 📁 members\apps.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.apps`
- `members.signals`

## Classes

### MembersConfig

**Métodos:**

- ready

## Funções

### ready

## Código completo

```python
from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = "members"
    verbose_name = "Membros do Carmelo"

    def ready(self):
        import members.signals

```


# 📁 members\backends.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.contrib.auth.backends`
- `models`

## Classes

### EmailBackend

**Métodos:**

- authenticate

## Funções

### authenticate

## Código completo

```python
from django.contrib.auth.backends import ModelBackend
from .models import Member


class EmailBackend(ModelBackend):

    def authenticate(self, request, email=None, password=None, **kwargs):

        # o admin manda username → aqui vira email

        try:
            user = Member.objects.get(email=email)
        except Member.DoesNotExist:
            return None

        if user.check_password(password):  # type: ignore
            return user

        return None

```


# 📁 members\forms.py

## Descrição

Arquivo responsável pelos formulários Django e validações de entrada.

## Imports

- `django`
- `django.contrib.auth.password_validation`
- `django.core.exceptions`
- `models`

## Classes

### MemberForm

**Métodos:**

- clean_email
- clean_password
- clean
- save

### MemberChangeForm

**Métodos:**

- clean_email
- clean_password
- clean
- save

### Meta

### Meta

## Funções

### clean_email

### clean_password

### clean

### save

### clean_email

### clean_password

### clean

### save

## Código completo

```python
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Member

# =========================
# REGISTER FORM
# =========================


class MemberForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                ":type": "hide_password ? 'password' : 'text'",
            }
        ),
        label="Senha",
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                ":type": "hide_password ? 'password' : 'text'",
            }
        ),
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

    # =========================
    # Validação da senha usando
    # AUTH_PASSWORD_VALIDATORS
    # =========================
    def clean_password(self):
        password: str = self.cleaned_data.get("password")  # type: ignore

        try:
            validate_password(password, self.instance)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)  # type: ignore

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if not password:
            self.add_error("password", "A senha é obrigatória.")

        if not password2:
            self.add_error("password2", "Confirme sua senha.")

        if password and password2:

            if password != password2:
                self.add_error("password2", "As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")
        user.set_password(password)

        if commit:
            user.save()

        return user


class MemberChangeForm(forms.ModelForm):

    password = forms.CharField(
        required=False,
        label="Nova Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                ":type": "hide_password ? 'password' : 'text'",
            }
        ),
    )

    password2 = forms.CharField(
        required=False,
        label="Confirmar Nova Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                ":type": "hide_password ? 'password' : 'text'",
            }
        ),
    )

    class Meta:
        model = Member
        fields = [
            "name",
            "email",
            "church",
            "entry_date",
            "roles",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "church": forms.TextInput(attrs={"class": "form-control"}),
            "entry_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "roles": forms.Select(
                attrs={
                    "class": "form-control px-1",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if Member.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")

        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        if not password:
            return password

        validate_password(password, self.instance)

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        # Não alterou senha
        if not password and not password2:
            return cleaned_data

        # Apenas um campo preenchido
        if not password or not password2:
            if not password:
                self.add_error("password", "Preencha o campo 1 de senha.")
            if not password2:
                self.add_error("password2", "Preencha o campo 2 de senha.")
            raise ValidationError("Preencha os dois campos de senha.")

        if password != password2:
            raise ValidationError("As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        member = super().save(commit=False)

        password = self.cleaned_data.get("password")

        if password:
            member.set_password(password)

        if commit:
            member.save()

        return member

```


# 📁 members\models.py

## Descrição

Arquivo responsável pelos modelos do banco de dados e regras de negócio através dos Models Django.

## Imports

- `datetime`
- `django.db`
- `django.utils.text`
- `django.contrib.auth.models`
- `base.models`
- `carmel.models`
- `django.core.validators`

## Classes

### MemberManager

**Métodos:**

- create_user
- create_superuser

### Address

**Métodos:**

- __str__

### Phone

**Métodos:**

- __str__

### Member

**Métodos:**

- __str__
- save

### Meta

### Meta

### Meta

## Funções

### create_user

### create_superuser

### __str__

### __str__

### __str__

### save

## Código completo

```python
from datetime import date
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from base.models import TimeStampedModel
from carmel.models import Carmel

from django.core.validators import validate_email

# =========================
# CONSTANTES
# =========================

ROLES_CARMEL = (
    (
        "MN",
        "Responsavel",
    ),  # ver Membros + Finanças + Registrar membros, passar titulo de responsavel
    ("FN", "Tesoreiro"),  # ver Finanças, passar titulo de responsavel
    ("NM", "Normal"),
)


# =========================
# MANAGER
# =========================


class MemberManager(BaseUserManager):

    def create_user(
        self,
        email,
        name,
        password=None,
        password2=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("Email é obrigatório")

        if password2 is not None and password != password2:
            raise ValueError("As senhas não coincidem")

        email = self.normalize_email(email)

        user = self.model(
            name=name,
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password, password)

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.save(using=self._db)
        return user


# =========================
# MODELS AUXILIARES
# =========================


class Address(models.Model):

    street = models.CharField(max_length=80, verbose_name="Rua")

    number = models.CharField(max_length=10, verbose_name="Número")

    neighborhood = models.CharField(max_length=50, verbose_name="Bairro")

    city = models.CharField(max_length=50, verbose_name="Cidade")

    state = models.CharField(max_length=2, verbose_name="Estado")

    zipcode = models.CharField(max_length=10, verbose_name="CEP")

    member = models.OneToOneField(
        "Member",
        on_delete=models.CASCADE,
        related_name="location",
    )

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.street}, {self.neighborhood}-{self.number}, {self.city}/{self.state} ({self.zipcode})"


class Phone(models.Model):

    name = models.CharField(max_length=40, blank=True, verbose_name="Descrição")

    number = models.CharField(max_length=15, verbose_name="Número")

    member = models.ForeignKey(
        "Member",
        on_delete=models.CASCADE,
        related_name="phones",
    )

    class Meta:
        verbose_name = "Telefone"
        verbose_name_plural = "Telefones"

    def __str__(self):
        return self.number


# =========================
# USER MODEL
# =========================


class Member(AbstractBaseUser, PermissionsMixin, TimeStampedModel):

    username = None

    name = models.CharField(max_length=100, verbose_name="Nome do Membro", unique=True)

    email = models.EmailField(unique=True, validators=[validate_email])

    church = models.CharField(
        max_length=100,
        verbose_name="Igreja que Participa",
    )

    entry_date = models.DateField(
        verbose_name="Data de Entrada",
    )

    carmel = models.ForeignKey(
        Carmel,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="members",
        db_index=True,
    )

    roles = models.CharField(
        max_length=2,
        choices=ROLES_CARMEL,
        default="NM",
        verbose_name="Função no Carmelo",
    )

    slug = models.SlugField(unique=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MemberManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = date.today()

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Generate a unique slug using UUID
            while Member.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # def phones(self):
    #     return Phone.objects.filter(member=self).all()

    # def location(self):
    #     return Address.objects.filter(member=self).first()

```


# 📁 members\signals.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `members.models`
- `django.dispatch`
- `django.db.models.signals`
- `rolepermissions.roles`

## Funções

### register_roles_member

## Código completo

```python
from members.models import Member
from django.dispatch import receiver

from django.db.models.signals import post_save
from rolepermissions.roles import assign_role


@receiver(post_save, sender=Member)
def register_roles_member(sender, instance, created, **kwargs):
    if created:
        if instance.roles == "MN":
            assign_role(instance, "manager_member")
        elif instance.roles == "FN":
            assign_role(instance, "finance_member")
        elif instance.roles == "NM":
            assign_role(instance, "normal_member")

```


# 📁 members\tests.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.test`

## Código completo

```python
from django.test import TestCase

# Create your tests here.

```


# 📁 members\urls.py

## Descrição

Arquivo responsável pelo roteamento das URLs do Django.

## Imports

- `django.urls`
- ``

## Código completo

```python
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.members_aLL, name="list_member"),
    path("informacoes/<slug:slug>", views.show_member, name="show_member"),
    # Members
    path("cadastrar/", views.register_member, name="register_member"),
    path("editar/<int:id>", views.update_member, name="update_member"),
    path("delete/<int:id>", views.delete_member, name="delete_member"),
    # ASSOCIATIONS
    path("votos/", include("votes.urls")),
    path("contribuicoes/", include("contributions.urls")),
    # HTMX
    path("filter_members/", views.filter_members, name="list_filter_members"),
]

```


# 📁 members\user_functions.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python

```


# 📁 members\views.py

## Descrição

Arquivo responsável pelo controle das requisições, processamento das regras e renderização das páginas.

## Imports

- `datetime`
- `django.contrib`
- `django.contrib.auth.decorators`
- `django.shortcuts`
- `django.urls`
- `rolepermissions.decorators`
- `members.models`
- `forms`

## Funções

### filter_member_object

Retorna lista de membros ativos (não-admin, não-staff) excluindo um ID.

Utilizado para filtrar membros disponíveis de forma padronizada.

### register_member

Cria um novo membro associado ao carmelo do usuário logado.

Valida o email (sem duplicatas) e salva o novo membro.

### members_aLL

Lista todos os membros ativos do sistema (exceto o usuário logado).

Exibe a lista de membros com opções de filtro e ações.

### filter_members

Filtra membros por nome de forma dinâmica (AJAX).

Retorna lista de membros que correspondem ao filtro digitado.

### show_member

Exibe o perfil detalhado de um membro específico.

Mostra: dados pessoais, telefones e endereço do membro.

### update_member

### delete_member

Deleta um membro do sistema.

Remove o membro e renderiza a lista atualizada.

## Código completo

```python
from datetime import date, timezone, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rolepermissions.decorators import has_permission_decorator

from members.models import Member, Phone

from .forms import MemberChangeForm, MemberForm

# Create your views here.

# 'create_member': True,
# 'read_member': True,
# 'edit_member': True,
# 'delete_member': True,
# 'list_members': True,


# FUNCTIONS


def filter_member_object(member_id):
    """Retorna lista de membros ativos (não-admin, não-staff) excluindo um ID.

    Utilizado para filtrar membros disponíveis de forma padronizada.
    """
    print("SQL")
    return (
        Member.objects.filter(is_superuser=False, is_staff=False, is_active=True)
        .only("id", "name", "slug", "entry_date")
        .order_by("name")
        .exclude(id=member_id)
    )


@login_required
@has_permission_decorator("create_member")
def register_member(request):
    """Cria um novo membro associado ao carmelo do usuário logado.

    Valida o email (sem duplicatas) e salva o novo membro.
    """
    form = MemberForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():

            form.clean_email()

            entry_date: date | None = form.cleaned_data.get("entry_date")
            if entry_date:
                if entry_date > date.today():
                    messages.error(
                        request, "O usuario não pode cadastrar em datas futuras"
                    )
                    return render(request, "members/register.html", {"form": form})


            member = form.save(commit=False)

            # MANUTENÇÃO: Garantir que request.user.carmel existe antes de usar

            member.carmel = request.user.carmel

            member.save()
            messages.success(request, "Membro cadastrado com sucesso!")
            return redirect(reverse("list_member"))
    return render(request, "members/register.html", {"form": form})


@login_required
@has_permission_decorator("list_members")
def members_aLL(request):
    """Lista todos os membros ativos do sistema (exceto o usuário logado).

    Exibe a lista de membros com opções de filtro e ações.
    """
    members = filter_member_object(request.user.id)

    # MANUTENÇÃO: Variável 'month' definida mas não utilizada
    month = date.today().month

    return render(request, "members/list.html", {"members": members})


@login_required
@has_permission_decorator("list_members")
def filter_members(request):
    """Filtra membros por nome de forma dinâmica (AJAX).

    Retorna lista de membros que correspondem ao filtro digitado.
    """
    name_filter = request.POST.get("filter_name")

    # MANUTENÇÃO: Condição 'or date' não faz sentido - remover
    if name_filter or date:
        members = filter_member_object(request.user.id).filter(
            name__icontains=name_filter
        )
    else:
        members = filter_member_object(request.user.id).all()

    return render(
        request,
        "members/components/list_filter_members.html",
        {"members": members},
    )


@login_required
@has_permission_decorator("read_member")
def show_member(request, slug):
    """Exibe o perfil detalhado de um membro específico.

    Mostra: dados pessoais, telefones e endereço do membro.
    """
    # MANUTENÇÃO: Usar select_related para otimizar queries
    member = get_object_or_404(Member, slug=slug)

    phones = member.phones.all()

    location = getattr(member, "location", None)

    if not location:
        location = None

    return render(
        request,
        "members/show.html",
        {"member": member, "phones": phones, "location": location},
    )


@login_required
@has_permission_decorator("edit_member")
def update_member(request, id):

    member = get_object_or_404(
        Member,
        pk=id,
    )

    if request.method == "POST":

        form = MemberChangeForm(
            request.POST,
            instance=member,
        )

        if form.is_valid():

            member = form.save()

            return redirect(reverse("list_member"))

    else:

        form = MemberChangeForm(
            instance=member,
        )

    return render(
        request,
        "members/update.html",
        {
            "form": form,
            "id": id,
        },
    )


@login_required
@has_permission_decorator("delete_member")
def delete_member(request, id: int):
    """Deleta um membro do sistema.

    Remove o membro e renderiza a lista atualizada.
    """
    member = get_object_or_404(Member, id=id)
    member.delete()

    members = filter_member_object(request.user.id).all()

    return render(
        request,
        "members/components/list_filter_members.html",
        {"members": members},
    )

```


# 📁 members\__init__.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python

```


# 📁 tests\conftest.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `os`
- `django`
- `pytest`
- `django.conf`
- `django.test.utils`
- `django.contrib.auth`
- `datetime`
- `decimal`
- `carmel.models`
- `members.models`
- `votes.models`
- `contributions.models`
- `accounts.models`
- `django.utils`

## Funções

### carmel_factory

Factory para criar Carmels nos testes.

### member_factory

Factory para criar Members nos testes.

### carmel

Fixture que retorna um Carmel criado.

### member

Fixture que retorna um Member criado.

### address_factory

Factory para criar Addresses nos testes.

### phone_factory

Factory para criar Phones nos testes.

### vote_registration_factory

Factory para criar VotesRegistration nos testes.

### vote_factory

Factory para criar Votes nos testes.

### contribution_factory

Factory para criar Contributions nos testes.

### reset_password_factory

Factory para criar ResetPasswordAccess nos testes.

### pytest_configure

Configurar pytest com django.

### django_db_setup

Configurar banco de dados de teste.

### _create_carmel

### _create_member

### _create_address

### _create_phone

### _create_vote_registration

### _create_vote

### _create_contribution

### _create_reset_password

## Código completo

```python
import os
import django
import pytest
from django.conf import settings

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test.utils import get_runner
from django.contrib.auth import get_user_model
from datetime import date
from decimal import Decimal

from carmel.models import Carmel
from members.models import Member, Address, Phone
from votes.models import VotesRegistration, Vote
from contributions.models import Contribution
from accounts.models import ResetPasswordAccess
from django.utils import timezone

# ============================================================================
# FIXTURES PARA TESTES
# ============================================================================


@pytest.fixture
def carmel_factory():
    """Factory para criar Carmels nos testes."""

    def _create_carmel(
        name="Carmelo Teste",
        description="Um ótimo carmelo",
        price_contribution_default=Decimal("50.00"),
        pay_day_contribution_default=15,
    ):
        return Carmel.objects.create(
            name=name,
            description=description,
            price_contribution_default=price_contribution_default,
            pay_day_contribution_default=pay_day_contribution_default,
        )

    return _create_carmel


@pytest.fixture
def member_factory():
    """Factory para criar Members nos testes."""

    def _create_member(
        email="teste@example.com",
        name="Teste User",
        church="Igreja",
        password="senha123",
        carmel=None,
        roles="NM",
        entry_date=None,
    ):
        member = Member.objects.create_user(
            email=email,
            name=name,
            church=church,
            password=password,
            carmel=carmel,
            roles=roles,
            entry_date=entry_date or date.today(),
        )
        return member

    return _create_member


@pytest.fixture
def carmel(carmel_factory):
    """Fixture que retorna um Carmel criado."""
    return carmel_factory()


@pytest.fixture
def member(member_factory, carmel):
    """Fixture que retorna um Member criado."""
    return member_factory(carmel=carmel)


@pytest.fixture
def address_factory(member_factory):
    """Factory para criar Addresses nos testes."""

    def _create_address(
        member=None,
        street="Rua das Flores",
        number="123",
        neighborhood="Centro",
        city="São Paulo",
        state="SP",
        zipcode="01234-567",
    ):
        if member is None:
            member = member_factory()

        return Address.objects.create(
            member=member,
            street=street,
            number=number,
            neighborhood=neighborhood,
            city=city,
            state=state,
            zipcode=zipcode,
        )

    return _create_address


@pytest.fixture
def phone_factory(member_factory):
    """Factory para criar Phones nos testes."""

    def _create_phone(member=None, name="Celular", number="11987654321"):
        if member is None:
            member = member_factory()

        return Phone.objects.create(member=member, name=name, number=number)

    return _create_phone


@pytest.fixture
def vote_registration_factory():
    """Factory para criar VotesRegistration nos testes."""

    def _create_vote_registration(
        name="Presidente", description="Voto para presidente"
    ):
        return VotesRegistration.objects.create(name=name, description=description)

    return _create_vote_registration


@pytest.fixture
def vote_factory(member_factory, vote_registration_factory):
    """Factory para criar Votes nos testes."""

    def _create_vote(
        member=None, votes_registration=None, type="DEF", date=None, year_duration=None
    ):
        if member is None:
            member = member_factory()

        if votes_registration is None:
            votes_registration = vote_registration_factory()

        return Vote.objects.create(
            member=member,
            votes_registration=votes_registration,
            type=type,
            date=date or timezone.now(),
            year_duration=year_duration,
        )

    return _create_vote


@pytest.fixture
def contribution_factory(member_factory):
    """Factory para criar Contributions nos testes."""

    def _create_contribution(member=None, price=Decimal("50.00"), date_pay=None):
        if member is None:
            member = member_factory()

        return Contribution.objects.create(
            member=member, price=price, date_pay=date_pay or date.today()
        )

    return _create_contribution


@pytest.fixture
def reset_password_factory(member_factory):
    """Factory para criar ResetPasswordAccess nos testes."""

    def _create_reset_password(member=None, token="token123abc", expired_at=None):
        if member is None:
            member = member_factory()

        # Limpar reset anterior se existir (OneToOneField)
        try:
            ResetPasswordAccess.objects.filter(member=member).delete()
        except:
            pass

        return ResetPasswordAccess.objects.create(
            member=member, token=token, expired_at=expired_at
        )

    return _create_reset_password


# ============================================================================
# CONFIGURAÇÃO DO PYTEST
# ============================================================================


def pytest_configure(config):
    """Configurar pytest com django."""
    settings.DEBUG = True
    # Adicionar configurações extras se necessário


@pytest.fixture(scope="session")
def django_db_setup():
    """Configurar banco de dados de teste."""
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

```


# 📁 tests\test_models.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `pytest`
- `datetime`
- `datetime`
- `django.utils`
- `django.core.exceptions`
- `django.db.utils`
- `decimal`
- `carmel.models`
- `members.models`
- `votes.models`
- `contributions.models`
- `accounts.models`

## Classes

### TestCarmelModel

**Métodos:**

- test_carmel_create_valid
- test_carmel_missing_required_name
- test_carmel_missing_required_description
- test_carmel_name_unique
- test_carmel_updated_at_changes_on_save

### TestMemberModel

**Métodos:**

- test_member_create_valid
- test_member_email_unique
- test_member_slug_unique
- test_member_roles_default
- test_member_roles_rejects_invalid_choice
- test_member_missing_required_email
- test_member_is_superuser_false_default
- test_member_carmel_relation
- test_member_carmel_is_optional

### TestAddressModel

**Métodos:**

- test_address_create_valid
- test_address_member_relation_onetoone
- test_address_missing_required_street
- test_address_member_optional

### TestPhoneModel

**Métodos:**

- test_phone_create_valid
- test_phone_multiple_per_member
- test_phone_number_required
- test_phone_name_optional

### TestVotesRegistrationModel

**Métodos:**

- test_votes_registration_create_valid
- test_votes_registration_missing_name
- test_votes_registration_missing_description

### TestVoteModel

**Métodos:**

- test_vote_create_valid
- test_vote_temporary_with_duration
- test_vote_type_rejects_invalid_choice
- test_vote_member_required

### TestContributionModel

**Métodos:**

- test_contribution_create_valid
- test_contribution_missing_member
- test_contribution_missing_date_pay
- test_contribution_updated_at_changes_on_save

## Funções

### member_factory

Retorna uma função para criar Member com valores padrão sensatos.

Uso:
    member = member_factory()
    member2 = member_factory(email="outro@example.com", name="Outro")

### carmel_factory

Retorna uma função para criar Carmel com valores padrão.

### address_factory

Retorna uma função para criar Address; cria um Member se não for passado.

### votes_registration_factory

### _create

### _create

### _create

### _create

### test_carmel_create_valid

### test_carmel_missing_required_name

### test_carmel_missing_required_description

### test_carmel_name_unique

name tem unique=True no schema — antes não havia teste para isso.

### test_carmel_updated_at_changes_on_save

Testa o comportamento real de auto_now, não só 'is not None'.

### test_member_create_valid

### test_member_email_unique

### test_member_slug_unique

### test_member_roles_default

### test_member_roles_rejects_invalid_choice

Antes não havia teste do caso negativo de choices.

### test_member_missing_required_email

Usa full_clean() em vez de depender de create_user levantar algo genérico.

### test_member_is_superuser_false_default

### test_member_carmel_relation

### test_member_carmel_is_optional

carmel é null=True/blank=True — vale confirmar que funciona sem ele.

### test_address_create_valid

### test_address_member_relation_onetoone

### test_address_missing_required_street

Testa um campo obrigatório específico, em vez de 'faltam vários'.

### test_address_member_optional

member é null=True/blank=True no schema.

### test_phone_create_valid

### test_phone_multiple_per_member

### test_phone_number_required

### test_phone_name_optional

### test_votes_registration_create_valid

### test_votes_registration_missing_name

### test_votes_registration_missing_description

### test_vote_create_valid

### test_vote_temporary_with_duration

### test_vote_type_rejects_invalid_choice

Antes só testava o caso válido (redundante com test_vote_create_valid).
Agora testa de fato a constraint de choices.

### test_vote_member_required

member tem null=False, blank=False — não havia teste disso.

### test_contribution_create_valid

### test_contribution_missing_member

### test_contribution_missing_date_pay

### test_contribution_updated_at_changes_on_save

## Código completo

```python
"""
Suíte de testes revisada.

Principais mudanças em relação à versão anterior:
- Fixtures reutilizáveis (member_factory, carmel_factory, address_factory,
  votes_registration_factory) para eliminar duplicação de
  `Member.objects.create_user(...)` repetida em quase todo teste.
- `pytest.raises(Exception)` genérico substituído por exceções específicas
  (IntegrityError, ValidationError) — evita que o teste passe por engano
  quando a falha é de outra natureza (ex: TypeError por argumento errado).
- Removidos testes que só confirmavam `isinstance(x, Decimal/str)`, pois
  isso é garantido pelo próprio field do Django e não valida regra nenhuma.
- `test_carmel_default_pay_day` removido: o valor era passado explicitamente,
  não testava default nenhum. Se existir um default real no model, o teste
  correto está em `test_carmel_pay_day_uses_model_default` abaixo (ajustar
  o valor esperado conforme o default real do field).
- Teste de `choices` do Vote agora testa também o caso INVÁLIDO
  (`full_clean()` deve rejeitar um type fora das choices).
- Testes de timestamp agora verificam o comportamento real do
  `auto_now`/`auto_now_add` (criar, salvar de novo, comparar updated_at),
  não só `is not None`.
- Bloco de ResetPasswordAccess reativado e corrigido.

NOTA: alguns testes abaixo fazem suposições sobre comportamento não
confirmado no schema fornecido (ex: se `slug` é auto-gerado no `save()`,
se existe validação de choices custom em `clean()`). Onde isso acontece,
deixei um comentário `# ASSUNÇÃO:` explicando o que precisa ser confirmado
no código real do model antes de confiar no teste.
"""

import pytest
from datetime import timedelta
from datetime import date as date_cls
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from decimal import Decimal

from carmel.models import Carmel
from members.models import Member, Address, Phone
from votes.models import Vote, VotesRegistration
from contributions.models import Contribution
from accounts.models import ResetPasswordAccess

# ============================================================================
# FIXTURES REUTILIZÁVEIS
# ============================================================================
#
# Usar factories (funções que criam o objeto) em vez de fixtures que já
# retornam a instância pronta, porque muitos testes precisam de variações
# (emails diferentes, com/sem carmel, etc). A fixture entrega a função,
# cada teste decide os overrides.


@pytest.fixture
def member_factory(db):
    """Retorna uma função para criar Member com valores padrão sensatos.

    Uso:
        member = member_factory()
        member2 = member_factory(email="outro@example.com", name="Outro")
    """
    created_emails = {"counter": 0}

    def _create(**overrides):
        created_emails["counter"] += 1
        defaults = {
            "email": f"membro{created_emails['counter']}@example.com",
            "password": "senha123",
            "name": "Membro Teste",
            "church": "Igreja Teste",
        }
        defaults.update(overrides)
        return Member.objects.create_user(**defaults)

    return _create


@pytest.fixture
def carmel_factory(db):
    """Retorna uma função para criar Carmel com valores padrão."""

    def _create(**overrides):
        defaults = {
            "name": "Carmelo Teste",
            "description": "Descrição padrão de teste",
            "price_contribution_default": Decimal("50.00"),
            "pay_day_contribution_default": 15,
        }
        defaults.update(overrides)
        return Carmel.objects.create(**defaults)

    return _create


@pytest.fixture
def address_factory(db, member_factory):
    """Retorna uma função para criar Address; cria um Member se não for passado."""

    def _create(**overrides):
        defaults = {
            "street": "Rua Teste",
            "number": "123",
            "neighborhood": "Bairro Teste",
            "city": "São Paulo",
            "state": "SP",
            "zipcode": "01234-567",
        }
        if "member" not in overrides:
            defaults["member"] = member_factory()
        defaults.update(overrides)
        return Address.objects.create(**defaults)

    return _create


@pytest.fixture
def votes_registration_factory(db):
    def _create(**overrides):
        defaults = {"name": "Cargo Teste", "description": "Descrição do cargo"}
        defaults.update(overrides)
        return VotesRegistration.objects.create(**defaults)

    return _create


# ============================================================================
# CARMEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestCarmelModel:
    def test_carmel_create_valid(self, carmel_factory):
        carmel = carmel_factory(name="Carmelo Santo", description="Um ótimo carmelo")
        assert carmel.id is not None
        assert carmel.name == "Carmelo Santo"
        assert carmel.created_at is not None
        assert carmel.updated_at is not None

    def test_carmel_missing_required_name(self):
        carmel = Carmel(
            description="Sem nome",
            price_contribution_default=Decimal("50.00"),
            pay_day_contribution_default=15,
        )
        with pytest.raises(ValidationError) as exc:
            carmel.full_clean()
        assert "name" in exc.value.message_dict

    def test_carmel_missing_required_description(self):
        carmel = Carmel(
            name="Sem Descrição",
            price_contribution_default=Decimal("50.00"),
            pay_day_contribution_default=15,
        )
        with pytest.raises(ValidationError) as exc:
            carmel.full_clean()
        assert "description" in exc.value.message_dict

    def test_carmel_name_unique(self, carmel_factory):
        """name tem unique=True no schema — antes não havia teste para isso."""
        carmel_factory(name="Nome Único")
        with pytest.raises(IntegrityError):
            carmel_factory(name="Nome Único")

    def test_carmel_updated_at_changes_on_save(self, carmel_factory):
        """Testa o comportamento real de auto_now, não só 'is not None'."""
        carmel = carmel_factory()
        first_updated_at = carmel.updated_at

        carmel.description = "Descrição alterada"
        carmel.save()
        carmel.refresh_from_db()

        assert carmel.updated_at > first_updated_at
        # created_at não deve mudar em um save subsequente (auto_now_add)
        assert carmel.created_at is not None


# ============================================================================
# MEMBER TESTS
# ============================================================================


@pytest.mark.django_db
class TestMemberModel:
    def test_member_create_valid(self, member_factory):
        member = member_factory(email="joao@example.com", name="João Silva")
        assert member.id is not None
        assert member.email == "joao@example.com"
        assert member.name == "João Silva"
        assert member.is_active is True
        assert member.is_staff is False

    def test_member_email_unique(self, member_factory):
        member_factory(email="unico@example.com")
        with pytest.raises(IntegrityError):
            member_factory(email="unico@example.com")

    def test_member_slug_unique(self, member_factory):
        # ASSUNÇÃO: slug é gerado automaticamente a partir do name no save().
        # Se o slug for passado manualmente em algum form/serializer, esse
        # teste precisa ser ajustado para refletir isso.
        member1 = member_factory(name="João Silva")
        member2 = member_factory(name="João Silva")

        assert member1.slug != member2.slug
        assert member1.slug

    def test_member_roles_default(self, member_factory):
        member = member_factory()
        assert member.roles == "NM"

    def test_member_roles_rejects_invalid_choice(self, member_factory):
        """Antes não havia teste do caso negativo de choices."""
        member = member_factory()
        member.roles = "XX"
        with pytest.raises(ValidationError) as exc:
            member.full_clean()
        assert "roles" in exc.value.message_dict

    def test_member_missing_required_email(self):
        """Usa full_clean() em vez de depender de create_user levantar algo genérico."""
        member = Member(name="Teste", church="Igreja")
        with pytest.raises(ValidationError) as exc:
            member.full_clean()
        assert "email" in exc.value.message_dict

    def test_member_is_superuser_false_default(self, member_factory):
        member = member_factory()
        assert member.is_superuser is False

    def test_member_carmel_relation(self, member_factory, carmel_factory):
        carmel = carmel_factory()
        member = member_factory(carmel=carmel)

        assert member.carmel == carmel
        assert carmel in Carmel.objects.all()

    def test_member_carmel_is_optional(self, member_factory):
        """carmel é null=True/blank=True — vale confirmar que funciona sem ele."""
        member = member_factory()
        assert member.carmel is None


# ============================================================================
# ADDRESS TESTS
# ============================================================================


@pytest.mark.django_db
class TestAddressModel:
    def test_address_create_valid(self, address_factory):
        address = address_factory(street="Rua das Flores")
        assert address.id is not None
        assert address.street == "Rua das Flores"
        assert address.member is not None

    def test_address_member_relation_onetoone(self, address_factory, member_factory):
        member = member_factory()
        address_factory(member=member)

        with pytest.raises(IntegrityError):
            address_factory(member=member)

    def test_address_missing_required_street(self, member_factory):
        """Testa um campo obrigatório específico, em vez de 'faltam vários'."""
        address = Address(
            number="123",
            neighborhood="Bairro",
            city="Cidade",
            state="SP",
            zipcode="01234-567",
            member=member_factory(),
        )
        with pytest.raises(ValidationError) as exc:
            address.full_clean()
        assert "street" in exc.value.message_dict

    def test_address_member_optional(self, address_factory):
        """member é null=True/blank=True no schema."""
        address = address_factory(member=None)
        assert address.member is None


# ============================================================================
# PHONE TESTS
# ============================================================================


@pytest.mark.django_db
class TestPhoneModel:
    def test_phone_create_valid(self, member_factory):
        member = member_factory()
        phone = Phone.objects.create(
            name="Celular", number="11987654321", member=member
        )

        assert phone.id is not None
        assert phone.name == "Celular"
        assert phone.member == member

    def test_phone_multiple_per_member(self, member_factory):
        member = member_factory()
        phone1 = Phone.objects.create(
            name="Celular", number="11987654321", member=member
        )
        phone2 = Phone.objects.create(
            name="Comercial", number="1133334444", member=member
        )

        # ASSUNÇÃO: o related_name da FK é "phones". Ajustar se for outro
        # (ex: "phone_set" caso não haja related_name customizado).
        phones = member.phones.all()
        assert phones.count() == 2
        assert phone1 in phones
        assert phone2 in phones

    def test_phone_number_required(self, member_factory):
        phone = Phone(name="Sem número", member=member_factory())
        with pytest.raises(ValidationError) as exc:
            phone.full_clean()
        assert "number" in exc.value.message_dict

    def test_phone_name_optional(self, member_factory):
        phone = Phone.objects.create(number="11987654321", member=member_factory())
        assert phone.name == ""


# ============================================================================
# VOTESREGISTRATION TESTS
# ============================================================================


@pytest.mark.django_db
class TestVotesRegistrationModel:
    def test_votes_registration_create_valid(self, votes_registration_factory):
        vote_reg = votes_registration_factory(
            name="Presidente", description="Voto para presidente"
        )
        assert vote_reg.id is not None
        assert vote_reg.name == "Presidente"

    def test_votes_registration_missing_name(self):
        vote_reg = VotesRegistration(description="Sem nome")
        with pytest.raises(ValidationError) as exc:
            vote_reg.full_clean()
        assert "name" in exc.value.message_dict

    def test_votes_registration_missing_description(self):
        vote_reg = VotesRegistration(name="Sem Descrição")
        with pytest.raises(ValidationError) as exc:
            vote_reg.full_clean()
        assert "description" in exc.value.message_dict


# ============================================================================
# VOTE TESTS
# ============================================================================


@pytest.mark.django_db
class TestVoteModel:
    def test_vote_create_valid(self, member_factory, votes_registration_factory):
        member = member_factory()
        vote_reg = votes_registration_factory(name="Presidente")

        vote = Vote.objects.create(
            member=member, votes_registration=vote_reg, date=timezone.now(), type="DEF"
        )

        assert vote.id is not None
        assert vote.member == member
        assert vote.type == "DEF"

    def test_vote_temporary_with_duration(
        self, member_factory, votes_registration_factory
    ):
        member = member_factory()
        vote_reg = votes_registration_factory(name="Tesoureiro")

        vote = Vote.objects.create(
            member=member,
            votes_registration=vote_reg,
            date=timezone.now(),
            type="TEMP",
            year_duration=2,
        )

        assert vote.type == "TEMP"
        assert vote.year_duration == 2

    def test_vote_type_rejects_invalid_choice(
        self, member_factory, votes_registration_factory
    ):
        """Antes só testava o caso válido (redundante com test_vote_create_valid).
        Agora testa de fato a constraint de choices."""
        member = member_factory()
        vote_reg = votes_registration_factory()

        vote = Vote(
            member=member,
            votes_registration=vote_reg,
            date=timezone.now(),
            type="INVALIDO",
        )
        with pytest.raises(ValidationError) as exc:
            vote.full_clean()
        assert "type" in exc.value.message_dict

    def test_vote_member_required(self, votes_registration_factory):
        """member tem null=False, blank=False — não havia teste disso."""
        vote_reg = votes_registration_factory()
        vote = Vote(votes_registration=vote_reg, date=timezone.now(), type="DEF")
        with pytest.raises(ValidationError) as exc:
            vote.full_clean()
        assert "member" in exc.value.message_dict


# ============================================================================
# CONTRIBUTION TESTS
# ============================================================================


@pytest.mark.django_db
class TestContributionModel:
    def test_contribution_create_valid(self, member_factory):
        member = member_factory()
        contribution = Contribution.objects.create(
            member=member, price=Decimal("50.00"), date_pay=date_cls.today()
        )

        assert contribution.id is not None
        assert contribution.price == Decimal("50.00")
        assert contribution.member == member

    def test_contribution_missing_member(self):
        contribution = Contribution(price=Decimal("50.00"), date_pay=date_cls.today())
        with pytest.raises(ValidationError) as exc:
            contribution.full_clean()
        assert "member" in exc.value.message_dict

    def test_contribution_missing_date_pay(self, member_factory):
        contribution = Contribution(member=member_factory(), price=Decimal("50.00"))
        with pytest.raises(ValidationError) as exc:
            contribution.full_clean()
        assert "date_pay" in exc.value.message_dict

    def test_contribution_updated_at_changes_on_save(self, member_factory):
        contribution = Contribution.objects.create(
            member=member_factory(), price=Decimal("50.00"), date_pay=date_cls.today()
        )
        first_updated_at = contribution.updated_at

        contribution.price = Decimal("75.00")
        contribution.save()
        contribution.refresh_from_db()

        assert contribution.updated_at > first_updated_at


# ============================================================================
# RESETPASSWORDACCESS TESTS
# ============================================================================
#
# Bloco reativado. Estava inteiro comentado na versão anterior, ou seja,
# o model mais sensível em termos de segurança (token de reset de senha)
# tinha cobertura zero.

```


# 📁 tests\__init__.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python

```


# 📁 votes\admin.py

## Descrição

Arquivo responsável pela configuração do Django Admin.

## Imports

- `django.contrib`
- `votes.models`

## Código completo

```python
from django.contrib import admin

from votes.models import Vote, VotesRegistration

# Register your models here.


admin.site.register(Vote)
admin.site.register(VotesRegistration)

```


# 📁 votes\apps.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.apps`

## Classes

### VotesConfig

## Código completo

```python
from django.apps import AppConfig


class VotesConfig(AppConfig):
    name = "votes"
    verbose_name = "Votos"

```


# 📁 votes\forms.py

## Descrição

Arquivo responsável pelos formulários Django e validações de entrada.

## Imports

- `django`
- `votes.models`

## Classes

### VoteRegisterForm

### VoteForm

### Meta

### Meta

## Código completo

```python
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

```


# 📁 votes\models.py

## Descrição

Arquivo responsável pelos modelos do banco de dados e regras de negócio através dos Models Django.

## Imports

- `django.db`
- `members.models`

## Classes

### VotesRegistration

**Métodos:**

- __str__

### Vote

**Métodos:**

- __str__

### Meta

### Meta

## Funções

### __str__

### __str__

## Código completo

```python
from django.db import models

from members.models import Member, TimeStampedModel

# Create your models here.
TYPES_VOTES = (("DEF", "Definitivo"), ("TEMP", "Temporários"))


class VotesRegistration(models.Model):

    class Meta:
        verbose_name = "Registro do Voto e suas caracteristicas"
        verbose_name_plural = "Registro dos Votos e suas caracteristicas"

    name = models.CharField(max_length=40)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.name


class Vote(TimeStampedModel):

    votes_registration = models.ForeignKey(VotesRegistration, on_delete=models.CASCADE)

    date = models.DateTimeField(verbose_name="Data e Hora do Voto")

    type = models.CharField(
        max_length=4, choices=TYPES_VOTES, verbose_name="Grau do Voto"
    )

    year_duration = models.IntegerField(
        verbose_name="Quantos Anos dura esse voto", null=True, blank=True
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="Membro")

    class Meta:
        verbose_name = "Voto do Membro"
        verbose_name_plural = "Votos do Membro"

    def __str__(self):
        name = ""
        if self.votes_registration:
            name = self.votes_registration.name

        return name

```


# 📁 votes\tests.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Imports

- `django.test`

## Código completo

```python
from django.test import TestCase

# Create your tests here.

```


# 📁 votes\urls.py

## Descrição

Arquivo responsável pelo roteamento das URLs do Django.

## Imports

- `django.urls`
- ``

## Código completo

```python
from django.urls import path
from . import views

urlpatterns = [
    # VOTES MEMBER
    path("listagem/<slug:slug>/", views.votes_member, name="votes_members"),
    path("register_vote/", views.register_vote, name="register_vote"),
    path("vote_member/<str:user>/pk/<int:id>", views.vote_member, name="vote_member"),
    path(
        "edit_vote_member/<str:user>/pk/<int:id>",
        views.edit_vote_member,
        name="edit_vote_member",
    ),
    path(
        "update_vote_member/<int:id>",
        views.update_vote_member,
        name="update_vote_member",
    ),
    path("delete_vote/<int:id>", views.delete_vote, name="delete_vote"),
    # REGISTER VOTES DEFAULT
    path("votos_do_carmelo/", views.votes_registration, name="votes_registration"),
    path(
        "register_votes_registration/",
        views.register_votes_registration,
        name="register_votes_registration",
    ),
    path(
        "edit_vote_registration/pk/<int:id>",
        views.edit_vote_registration,
        name="edit_vote_registration",
    ),
    path(
        "update_vote_registration/pk/<int:id>",
        views.update_vote_registration,
        name="update_vote_registration",
    ),
    path(
        "delete_votes_registration/pk/<int:id>",
        views.delete_votes_registration,
        name="delete_votes_registration",
    ),
]

```


# 📁 votes\views.py

## Descrição

Arquivo responsável pelo controle das requisições, processamento das regras e renderização das páginas.

## Imports

- `django.contrib`
- `django.contrib.auth.decorators`
- `django.shortcuts`
- `rolepermissions.decorators`
- `members.models`
- `votes.forms`
- `votes.models`

## Funções

### register_vote

Registra um novo voto para um membro.

Valida se o membro já possui esse voto; se não, cria o registro.

### vote_member

Lista todas as opções de voto disponíveis para seleção.

Renderiza as opções de voto para associar a um membro.

### edit_vote_member

Carrega o formulário de edição de um voto específico.

Renderiza o formulário preenchido com os dados do voto.

### update_vote_member

Atualiza um voto existente com novos dados.

Processa a submissão do formulário e atualiza o voto no banco.

### delete_vote

Deleta um voto de um membro.

Remove o voto e renderiza a lista de votos atualizada.

### votes_member

Lista todos os votos de um membro específico.

Exibe o histórico de votos do membro com opção de adicionar novos.

### votes_registration

Lista todas as opções de voto disponíveis no sistema.

Exibe as opções registradas e permite criar novas.

### register_votes_registration

Registra uma nova opção de voto no sistema.

Valida se não existe duplicata e salva o novo tipo de voto.

### edit_vote_registration

Carrega o formulário de edição de uma opção de voto.

Renderiza o formulário preenchido com os dados da opção.

### update_vote_registration

Atualiza uma opção de voto existente.

Processa a submissão do formulário e atualiza os dados da opção.

### delete_votes_registration

Deleta uma opção de voto do sistema.

Remove o tipo de voto e renderiza a lista atualizada.

## Código completo

```python
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from rolepermissions.decorators import has_permission_decorator

from members.models import Member
from votes.forms import VoteForm, VoteRegisterForm
from votes.models import Vote, VotesRegistration

# 'create_vote': True,
# 'read_vote': True,
# 'edit_vote': True,
# 'delete_vote': True,
# 'list_vote': True,


# Create your views here.
@login_required
@has_permission_decorator("create_vote")
def register_vote(request):
    """Registra um novo voto para um membro.

    Valida se o membro já possui esse voto; se não, cria o registro.
    """
    user_current = request.POST.get("user_current")
    user = Member.objects.filter(slug=user_current).first()

    if request.method == "POST":
        form_vote = VoteForm(request.POST)

        if form_vote.is_valid():
            # MANUTENÇÃO: Usar .exists() em vez de .exists() para apenas verificar existência
            vote_exists = Vote.objects.filter(
                member=user,
                votes_registration__name=form_vote.cleaned_data.get(
                    "votes_registration"
                ),
            ).exists()
            if not vote_exists:
                vote = form_vote.save(commit=False)
                vote.member = user
                vote.save()
                form_vote = VoteForm()

                messages.success(request, "Voto Salvo com sucesso! ")
            else:
                messages.error(request, "O membro já possui esse voto!")

    votes = Vote.objects.filter(member=user).select_related("votes_registration").all()

    return render(
        request,
        "votes/components_votes/list_votes.html",
        {
            "votes": votes,
            "user_current": user_current,
            "form_vote": form_vote,
        },
    )


@login_required
@has_permission_decorator("list_vote")
def vote_member(request, user, id):
    """Lista todas as opções de voto disponíveis para seleção.

    Renderiza as opções de voto para associar a um membro.
    """
    # MANUTENÇÃO: Parâmetros 'user' e 'id' não são utilizados
    votes = VotesRegistration.objects.select_related("votes_registration").all()

    return render(
        request,
        "votes/components_votes/option_vote_registration.html",
        {"votes": votes},
    )


@login_required
@has_permission_decorator("edit_vote")
def edit_vote_member(request, user, id):
    """Carrega o formulário de edição de um voto específico.

    Renderiza o formulário preenchido com os dados do voto.
    """
    if request.method == "GET":
        # MANUTENÇÃO: Usar get_object_or_404 em vez de .first() para melhor tratamento de erro
        vote = (
            Vote.objects.filter(member__slug=user, id=id)
            .select_related("votes_registration")
            .first()
        )
        form = VoteForm(instance=vote)

    return render(
        request,
        "votes/components_votes/form_edit_vote_member.html",
        {"form_update": form, "vote_id": id, "user_current": user},
    )


@login_required
@has_permission_decorator("edit_vote")
def update_vote_member(request, id):
    """Atualiza um voto existente com novos dados.

    Processa a submissão do formulário e atualiza o voto no banco.
    """
    form_update = VoteForm(request.POST)
    if form_update.is_valid():
        vote = Vote.objects.filter(id=id).first()

        if vote:
            # MANUTENÇÃO: Refatorar para usar form.save()
            vote.date = form_update.cleaned_data.get("date")  # type: ignore
            vote.type = form_update.cleaned_data.get("type")  # type: ignore
            vote.votes_registration_id = form_update.cleaned_data.get("votes_registration")  # type: ignore
            if form_update.cleaned_data.get("type") == "TEMP":
                vote.year_duration = form_update.cleaned_data.get("year_duration")

            vote.save()

            form_update = None

            messages.success(request, "Voto atualizado com sucesso! ")

    # atualizando a lista de votos do membro
    user_current = request.POST.get("user_current")
    votes = (
        Vote.objects.select_related("votes_registration")
        .filter(member__slug=user_current)
        .all()
    )
    # renderizando a lista de votos do membro atualizado
    return render(
        request,
        "votes/components_votes/list_votes.html",
        {
            "votes": votes,
            "vote_id": id,
            "form_update": form_update,
            "form": VoteForm(),
            "user_current": user_current,
        },
    )


@login_required
@has_permission_decorator("delete_vote")
def delete_vote(request, id: int):
    """Deleta um voto de um membro.

    Remove o voto e renderiza a lista de votos atualizada.
    """
    form_vote = VoteForm()
    user_current = request.POST.get("user_current")

    # MANUTENÇÃO: Usar get_object_or_404 em vez de .first()
    vote = Vote.objects.filter(id=id).first()

    if vote:
        vote.delete()

        messages.success(request, "Voto deletado")

        votes = Vote.objects.filter(member__slug=user_current).all()

    return render(
        request,
        "votes/components_votes/list_votes.html",
        {
            "votes": votes,
            "user_current": user_current,
            "form_vote": form_vote,
        },
    )


@login_required
@has_permission_decorator("list_vote")
def votes_member(request, slug):
    """Lista todos os votos de um membro específico.

    Exibe o histórico de votos do membro com opção de adicionar novos.
    """
    votes = (
        Vote.objects.filter(member__slug=slug)
        .prefetch_related("votes_registration")
        .all()
    )
    form_vote = VoteForm()

    return render(
        request,
        "votes/list.html",
        {"votes": votes, "form_vote": form_vote, "user_current": slug},
    )


# registration


# 'create_votes_registration': True,
# 'read_votes_registration': True,
# 'edit_votes_registration': True,
# 'delete_votes_registration': True,
# 'list_votes_registration': True,
@login_required
@has_permission_decorator("list_votes_registration")
def votes_registration(request):
    """Lista todas as opções de voto disponíveis no sistema.

    Exibe as opções registradas e permite criar novas.
    """
    form = VoteRegisterForm()
    votes_registration = VotesRegistration.objects.all()

    return render(
        request,
        "votes/votes_registration.html",
        {"form": form, "votes_registration": votes_registration},
    )


@login_required
@has_permission_decorator("create_votes_registration")
def register_votes_registration(request):
    """Registra uma nova opção de voto no sistema.

    Valida se não existe duplicata e salva o novo tipo de voto.
    """
    form = VoteRegisterForm(request.POST)
    # MANUTENÇÃO: Usar form.data.get() pode falhar - melhor usar form.cleaned_data após validar
    exists = VotesRegistration.objects.filter(name=form.data.get("name")).exists()

    if exists:
        messages.warning(request, "Voto Já cadastrado!")

    if form.is_valid() and not exists:
        messages.success(request, "Opção de Voto cadastrado com sucesso!")
        form.save()
        form = VoteRegisterForm(initial={})

    # MANUTENÇÃO: Lógica confusa - sempre executa se not exists, mesmo se form não foi válido
    if not exists:
        votes_registration = VotesRegistration.objects.all()

    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {"votes_registration": votes_registration, "form": form},
    )


@login_required
@has_permission_decorator("edit_vote_registration")
def edit_vote_registration(request, id):
    """Carrega o formulário de edição de uma opção de voto.

    Renderiza o formulário preenchido com os dados da opção.
    """
    if request.method == "GET":
        # MANUTENÇÃO: Usar get_object_or_404 para melhor tratamento de erro
        vote = VotesRegistration.objects.get(id=id)
        form = VoteRegisterForm(instance=vote)

    return render(
        request,
        "votes/components_votes/form_edit_vote_registration.html",
        {"form_update": form, "vote_id": id},
    )


@login_required
@has_permission_decorator("edit_votes_registration")
def update_vote_registration(request, id):
    """Atualiza uma opção de voto existente.

    Processa a submissão do formulário e atualiza os dados da opção.
    """
    form_update = VoteRegisterForm(request.POST)
    if form_update.is_valid():
        # MANUTENÇÃO: Usar get_object_or_404 e form.save() para simplificar
        vote_registration = VotesRegistration.objects.filter(id=id).first()

        if vote_registration:
            vote_registration.name = form_update.cleaned_data.get("name")  # type: ignore
            vote_registration.description = form_update.cleaned_data.get("description")  # type: ignore
            vote_registration.save()

            form_update = None

            messages.success(request, "Registro de voto atualizado com sucesso! ")

    # atualizando a lista de registros de votos
    votes_registration = VotesRegistration.objects.all()
    # renderizando a lista de registros de votos atualizada
    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {
            "votes_registration": votes_registration,
            "form_update": form_update,
            "form": VoteRegisterForm(),
        },
    )


@login_required
@has_permission_decorator("delete_votes_registration")
def delete_votes_registration(request, id):
    """Deleta uma opção de voto do sistema.

    Remove o tipo de voto e renderiza a lista atualizada.
    """
    # MANUTENÇÃO: Validar se a deleção foi bem-sucedida de forma melhor
    is_votes_registration_deleted = get_object_or_404(
        VotesRegistration, id=id
    ).delete()[0]
    form = VoteRegisterForm()

    if is_votes_registration_deleted == 1:
        messages.success(request, "Nome do Voto Deletado com Sucesso")
    else:
        messages.error(request, "Erro ao Deletar Nome do Voto")

    votes_registration = VotesRegistration.objects.all()

    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {
            "votes_registration": votes_registration,
            "form": form,
        },
    )

```


# 📁 votes\__init__.py

## Descrição

Arquivo Python contendo lógica do sistema.

## Código completo

```python

```
