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
            entry_date: date | None = form.cleaned_data.get("entry_date")
            if entry_date:
                if entry_date > date.today():
                    messages.error(
                        request, "O usuario não pode cadastrar em datas futuras"
                    )
                    return render(request, "members/register.html", {"form": form})
            form.clean_email()
            form.clean()

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
