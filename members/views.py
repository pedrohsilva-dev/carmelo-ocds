from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rolepermissions.decorators import has_permission_decorator

from contributions.models import Contribution
from members.models import Member, Phone, ROLES_CARMEL

from .forms import MemberChangeForm, MemberForm

# Create your views here.

# 'create_member': True,
# 'read_member': True,
# 'edit_member': True,
# 'delete_member': True,
# 'list_members': True,


# FUNCTIONS


def filter_member_object(member_id, carmel):
    """Retorna lista de membros do Carmelo, excluindo um ID de usuário.

    Não inclui administradores ou staff.
    """
    return (
        Member.objects.filter(
            is_superuser=False,
            is_staff=False,
            carmel=carmel,
        )
        .only("id", "name", "slug", "entry_date", "roles", "is_active")
        .order_by("name")
        .exclude(id=member_id)
    )


def get_member_pending_counts(members):
    """Retorna contagem de meses pendentes por membro."""
    today = date.today()
    member_ids = [member.pk for member in members]
    if not member_ids:
        return {}

    contributions = (
        Contribution.objects.filter(
            member_id__in=member_ids,
            date_pay__lte=today,
        )
        .values("member_id", "date_pay__year", "date_pay__month")
        .distinct()
    )

    paid_months = {}
    for contrib in contributions:
        paid_months.setdefault(contrib["member_id"], set()).add(
            (contrib["date_pay__year"], contrib["date_pay__month"])
        )

    pending = {}
    for member in members:
        start_year = member.entry_date.year
        start_month = member.entry_date.month
        expected_months = 0
        current_year = today.year
        current_month = today.month

        year = start_year
        month = start_month
        while (year, month) <= (current_year, current_month):
            expected_months += 1
            month += 1
            if month > 12:
                month = 1
                year += 1

        paid = len(paid_months.get(member.pk, set()))
        missing = max(0, expected_months - paid)
        pending[member.pk] = {
            "pending_count": missing,
            "has_pending": missing > 0,
        }

    return pending


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
    """Lista membros do Carmelo com filtros e paginação."""
    filter_name = request.GET.get("filter_name", "").strip()
    filter_role = request.GET.get("filter_role", "")
    filter_active = request.GET.get("filter_active", "active")
    filter_pending = request.GET.get("filter_pending", "")
    page = request.GET.get("page", 1)

    members = filter_member_object(request.user.id, request.user.carmel)

    if filter_name:
        members = members.filter(name__icontains=filter_name)

    if filter_role:
        members = members.filter(roles=filter_role)

    if filter_active == "active":
        members = members.filter(is_active=True)
    elif filter_active == "inactive":
        members = members.filter(is_active=False)

    member_list = list(members)
    pending_data = get_member_pending_counts(member_list)

    for member in member_list:
        stats = pending_data.get(member.pk, {})
        setattr(member, "pending_count", stats.get("pending_count", 0))
        setattr(member, "has_pending", stats.get("has_pending", False))

    if filter_pending == "yes":
        member_list = [
            m for m in member_list if pending_data.get(m.pk, {}).get("has_pending")
        ]

    total_members = len(member_list)
    pending_members = sum(1 for m in member_list if getattr(m, "has_pending", False))
    no_pending_members = total_members - pending_members

    paginator = Paginator(member_list, 12)
    page_obj = paginator.get_page(page)

    total_pending_members = sum(
        1 for stats in pending_data.values() if stats["has_pending"]
    )

    return render(
        request,
        "members/list.html",
        {
            "members": page_obj,
            "page_obj": page_obj,
            "filter_name": filter_name,
            "filter_role": filter_role,
            "filter_active": filter_active,
            "filter_pending": filter_pending,
            "roles_choices": ROLES_CARMEL,
            "pending_data": pending_data,
            "total_pending_members": total_pending_members,
        },
    )


@login_required
@has_permission_decorator("list_members")
def filter_members(request):
    """Filtra membros por nome de forma dinâmica (AJAX).

    Retorna lista de membros que correspondem ao filtro digitado.
    """
    name_filter = request.GET.get("filter_name", "").strip()
    filter_role = request.GET.get("filter_role", "")
    filter_active = request.GET.get("filter_active", "active")
    filter_pending = request.GET.get("filter_pending", "")

    members = filter_member_object(request.user.id, request.user.carmel)

    if name_filter:
        members = members.filter(name__icontains=name_filter)

    if filter_role:
        members = members.filter(roles=filter_role)

    if filter_active == "active":
        members = members.filter(is_active=True)
    elif filter_active == "inactive":
        members = members.filter(is_active=False)

    member_list = list(members)
    pending_data = get_member_pending_counts(member_list)

    for member in member_list:
        stats = pending_data.get(member.pk, {})
        setattr(member, "pending_count", stats.get("pending_count", 0))
        setattr(member, "has_pending", stats.get("has_pending", False))

    if filter_pending == "yes":
        member_list = [
            m for m in member_list if pending_data.get(m.pk, {}).get("has_pending")
        ]

    total_members = len(member_list)
    pending_members = sum(1 for m in member_list if getattr(m, "has_pending", False))
    no_pending_members = total_members - pending_members

    paginator = Paginator(member_list, 12)
    page = request.GET.get("page", 1)
    page_obj = paginator.get_page(page)

    return render(
        request,
        "members/components/list_filter_members.html",
        {
            "members": page_obj,
            "page_obj": page_obj,
            "filter_name": name_filter,
            "filter_role": filter_role,
            "filter_active": filter_active,
            "filter_pending": filter_pending,
            "roles_choices": ROLES_CARMEL,
            "pending_data": pending_data,
            "pending_members": pending_members,
            "no_pending_members": no_pending_members,
        },
    )


@login_required
@has_permission_decorator("read_member")
def show_member(request, slug):
    """Exibe o perfil detalhado de um membro específico.

    Mostra: dados pessoais, telefones e endereço do membro.
    """
    member = get_object_or_404(Member, slug=slug, carmel=request.user.carmel)

    phones_manager = getattr(member, "phones", None)
    phones = phones_manager.all() if phones_manager is not None else []

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
        carmel=request.user.carmel,
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
    member = get_object_or_404(Member, id=id, carmel=request.user.carmel)
    member.delete()

    members = filter_member_object(request.user.id, request.user.carmel)
    member_list = list(members)
    pending_data = get_member_pending_counts(member_list)

    for member in member_list:
        stats = pending_data.get(member.pk, {})
        setattr(member, "pending_count", stats.get("pending_count", 0))
        setattr(member, "has_pending", stats.get("has_pending", False))

    total_members = len(member_list)
    pending_members = sum(1 for m in member_list if getattr(m, "has_pending", False))
    no_pending_members = total_members - pending_members

    paginator = Paginator(member_list, 12)
    page_obj = paginator.get_page(1)

    return render(
        request,
        "members/components/list_filter_members.html",
        {
            "members": page_obj,
            "page_obj": page_obj,
            "filter_name": "",
            "filter_role": "",
            "filter_active": "active",
            "filter_pending": "",
            "roles_choices": ROLES_CARMEL,
            "pending_data": pending_data,
            "total_pending_members": sum(
                1 for stats in pending_data.values() if stats["has_pending"]
            ),
            "pending_members": pending_members,
            "no_pending_members": no_pending_members,
        },
    )
