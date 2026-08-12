from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rolepermissions.decorators import has_permission_decorator

from carmel.models import Carmel
from members.models import Member, ROLES_CARMEL

from .forms import MemberChangeForm, MemberForm
from .services import (
    available_carmels,
    decorate_members_with_pending,
    filter_carmel_members,
    get_member_pending_counts,
    transfer_member_to_carmel,
)

# Create your views here.

# 'create_member': True,
# 'read_member': True,
# 'edit_member': True,
# 'delete_member': True,
# 'list_members': True,


# ==========================================================
# HELPERS DE VIEW
# ==========================================================


def _apply_filters(members, request):
    """Aplica os filtros de nome, função, status e pendências."""
    filter_name = request.GET.get("filter_name", "").strip()
    filter_role = request.GET.get("filter_role", "")
    filter_active = request.GET.get("filter_active", "active")
    filter_pending = request.GET.get("filter_pending", "")

    if filter_name:
        members = members.filter(name__icontains=filter_name)

    if filter_role:
        members = members.filter(roles=filter_role)

    if filter_active == "active":
        members = members.filter(is_active=True)
    elif filter_active == "inactive":
        members = members.filter(is_active=False)

    return members, filter_name, filter_role, filter_active, filter_pending


def _member_list_context(member_list, pending_data, page=1, **extra):
    """Monta o contexto comum das listagens de membros."""
    paginator = Paginator(member_list, 12)
    page_obj = paginator.get_page(page)

    pending_members = sum(1 for m in member_list if getattr(m, "has_pending", False))
    no_pending_members = len(member_list) - pending_members
    total_pending_members = sum(
        1 for stats in pending_data.values() if stats["has_pending"]
    )

    context = {
        "members": page_obj,
        "page_obj": page_obj,
        "roles_choices": ROLES_CARMEL,
        "pending_data": pending_data,
        "total_pending_members": total_pending_members,
        "pending_members": pending_members,
        "no_pending_members": no_pending_members,
    }
    context.update(extra)
    return context


# ==========================================================
# MEMBERS
# ==========================================================


@login_required
@has_permission_decorator("create_member")
def register_member(request):
    """Cria um novo membro associado ao carmelo do usuário logado."""
    if not request.user.carmel:
        messages.error(
            request,
            "Usuário incompleto para cadastrar membros. Entre em contato com o administrador do sistema.",
        )
        return redirect("/")

    form = MemberForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        entry_date = form.cleaned_data.get("entry_date")
        if entry_date and entry_date > date.today():
            messages.error(request, "O usuário não pode cadastrar em datas futuras.")
            return render(request, "members/register.html", {"form": form})

        member = form.save(commit=False)
        member.carmel = request.user.carmel
        member.save()
        messages.success(request, "Membro cadastrado com sucesso!")
        return redirect(reverse("list_member"))

    return render(request, "members/register.html", {"form": form})


@login_required
@has_permission_decorator("list_members")
def members_aLL(request):
    """Lista membros do Carmelo com filtros e paginação."""
    members = filter_carmel_members(request.user.carmel, exclude_id=request.user.id)
    members, filter_name, filter_role, filter_active, filter_pending = _apply_filters(
        members, request
    )

    member_list = list(members)
    pending_data = get_member_pending_counts(member_list)
    member_list = decorate_members_with_pending(member_list, pending_data)

    if filter_pending == "yes":
        member_list = [m for m in member_list if getattr(m, "has_pending", False)]

    page = request.GET.get("page", 1)

    context = _member_list_context(
        member_list,
        pending_data,
        page=page,
        filter_name=filter_name,
        filter_role=filter_role,
        filter_active=filter_active,
        filter_pending=filter_pending,
    )
    return render(request, "members/list.html", context)


@login_required
@has_permission_decorator("list_members")
def filter_members(request):
    """Filtra membros por nome/função/status de forma dinâmica (HTMX)."""
    members = filter_carmel_members(request.user.carmel, exclude_id=request.user.id)
    members, filter_name, filter_role, filter_active, filter_pending = _apply_filters(
        members, request
    )

    member_list = list(members)
    pending_data = get_member_pending_counts(member_list)
    member_list = decorate_members_with_pending(member_list, pending_data)

    if filter_pending == "yes":
        member_list = [m for m in member_list if getattr(m, "has_pending", False)]

    page = request.GET.get("page", 1)

    context = _member_list_context(
        member_list,
        pending_data,
        page=page,
        filter_name=filter_name,
        filter_role=filter_role,
        filter_active=filter_active,
        filter_pending=filter_pending,
    )
    return render(request, "members/components/list_filter_members.html", context)


@login_required
@has_permission_decorator("read_member")
def show_member(request, slug):
    """Exibe o perfil detalhado de um membro específico."""
    member = get_object_or_404(Member, slug=slug, carmel=request.user.carmel)
    phones = member.phones.all()
    location = member.address_or_none

    return render(
        request,
        "members/show.html",
        {"member": member, "phones": phones, "location": location},
    )


@login_required
@has_permission_decorator("edit_member")
def update_member(request, id):
    member = get_object_or_404(Member, pk=id, carmel=request.user.carmel)

    if request.method == "POST":
        form = MemberChangeForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Membro atualizado com sucesso!")
            return redirect(reverse("list_member"))
    else:
        form = MemberChangeForm(instance=member)

    return render(
        request,
        "members/update.html",
        {"form": form, "id": id, "member": member},
    )


@login_required
@has_permission_decorator("delete_member")
def delete_member(request, id: int):
    """Deleta um membro do sistema e devolve a lista atualizada (HTMX)."""
    member = get_object_or_404(Member, id=id, carmel=request.user.carmel)
    member.delete()
    messages.success(request, "Membro removido com sucesso.")

    members = filter_carmel_members(request.user.carmel, exclude_id=request.user.id)
    member_list = list(members)
    pending_data = get_member_pending_counts(member_list)
    member_list = decorate_members_with_pending(member_list, pending_data)

    context = _member_list_context(
        member_list,
        pending_data,
        page=1,
        filter_name="",
        filter_role="",
        filter_active="active",
        filter_pending="",
    )
    return render(request, "members/components/list_filter_members.html", context)


# ==========================================================
# TRANSFERÊNCIA DE CARMELO
# ==========================================================


@login_required
@has_permission_decorator("transfer_carmel")
def transfer_member(request, id):
    """Transfere um membro para outro carmelo (fluxo do responsável)."""
    member = get_object_or_404(Member, id=id, carmel=request.user.carmel)

    if request.method == "POST":
        target_carmel = get_object_or_404(Carmel, pk=request.POST.get("target_carmel"))

        if target_carmel.pk == member.carmel_id:
            messages.warning(request, "O membro já pertence a este carmelo.")
        else:
            old_carmel = member.carmel
            transfer_member_to_carmel(member, target_carmel)
            messages.success(
                request,
                f"{member.name} foi transferido de {old_carmel} para {target_carmel}.",
            )

        # Após a transferência o membro sai do escopo do carmelo do gestor
        return redirect(reverse("list_member"))

    context = {
        "member": member,
        "carmels": available_carmels(exclude_carmel=member.carmel),
    }
    return render(request, "members/transfer.html", context)
