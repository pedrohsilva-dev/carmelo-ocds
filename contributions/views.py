from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rolepermissions.checkers import has_permission
from rolepermissions.decorators import has_permission_decorator

from base.utils import paginate
from carmel.models import Carmel
from contributions.forms import ContributionForm
from contributions.models import Contribution
from contributions.services import get_financial_summary, month_empty
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

    Valida data (entre entrada do membro e hoje), valor (limites) e mês único.
    """
    member = get_object_or_404(Member, slug=user, carmel=request.user.carmel)
    carmel: Carmel = request.user.carmel

    form = ContributionForm(request.POST or None, member=member)

    date_entry = member.entry_date
    date_now = date.today()

    if request.method == "POST" and form.is_valid():
        price = form.cleaned_data["price"]

        try:
            with transaction.atomic():
                contrib: Contribution = form.save(commit=False)

                contrib.member = member
                if not price:
                    contrib.price = carmel.price_contribution_default
                    messages.info(request, "Foi cadastrado com valor padrão do carmelo.")

                contrib.carmel = carmel

                # Executa as validações do model (mês único)
                contrib.full_clean()

                contrib.save()

                messages.success(request, "Contribuição cadastrada com sucesso.")

                form = ContributionForm(member=member)

        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)

    contributions = paginate(
        Contribution.objects.filter(member=member).order_by("-date_pay"),
        request,
        per_page=10,
    )
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
            "months": month_data,
        },
    )


@login_required
@has_permission_decorator("edit_contribute")
def edit_contribution(request, user, id):
    """Carrega o formulário de edição de uma contribuição (HTMX)."""
    contribution = get_object_or_404(
        Contribution,
        id=id,
        member__slug=user,
        member__carmel=request.user.carmel,
    )

    form_update = ContributionForm(instance=contribution, member=contribution.member)

    return render(
        request,
        "contribution/components_contribution/form_edit_contribution.html",
        {
            "form_update": form_update,
            "contribution_id": id,
            "user_current": user,
        },
    )


@login_required
@has_permission_decorator("edit_contribute")
def update_contribution(request, user, id):
    """Atualiza uma contribuição existente e devolve a lista (HTMX)."""
    contribution = get_object_or_404(
        Contribution,
        id=id,
        member__slug=user,
        member__carmel=request.user.carmel,
    )
    member = contribution.member
    carmel: Carmel = request.user.carmel

    form_update = ContributionForm(
        request.POST or None,
        instance=contribution,
        member=member,
    )

    if form_update.is_valid():
        price = form_update.cleaned_data["price"]

        try:
            with transaction.atomic():
                contrib = form_update.save(commit=False)

                # Campo vazio na edição → mantém o valor já registrado
                if not price:
                    contrib.price = contribution.price

                contrib.carmel = carmel

                # Valida mês único (o model ignora o próprio registro na edição)
                contrib.full_clean()

                contrib.save()

                messages.success(request, "Contribuição atualizada com sucesso.")

        except ValidationError as exc:
            # Erros do model (ex: mês duplicado) vão para o FORM, não só para
            # messages: o HTMX troca apenas #list-contribution, e o bloco de
            # messages fica fora desse alvo — sem add_error o usuário não
            # veria o erro dentro do modal.
            for field, msgs in exc.message_dict.items():
                for msg in msgs:
                    form_update.add_error(field, msg)
            for error in exc.messages:
                messages.error(request, error)

    member = contribution.member
    form = ContributionForm(member=member)
    contributions = paginate(
        Contribution.objects.filter(member=member).order_by("-date_pay"),
        request,
        per_page=10,
    )
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
            "months": month_data,
            "form_update": form_update if form_update.errors else None,
            "contribution_id": contribution.pk if form_update.errors else None,
        },
    )


@login_required
@has_permission_decorator("delete_contribute")
def delete_contribution(request, user, id):
    """Deleta uma contribuição de um membro e devolve a lista (HTMX)."""
    contribution = get_object_or_404(
        Contribution, id=id, member__carmel=request.user.carmel
    )

    contribution.delete()
    messages.success(request, "Contribuição deletada com sucesso.")

    member = get_object_or_404(Member, slug=user, carmel=request.user.carmel)
    carmel: Carmel = request.user.carmel

    form = ContributionForm(member=member)
    contributions = paginate(
        Contribution.objects.filter(member=member).order_by("-date_pay"),
        request,
        per_page=10,
    )
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
            "months": month_data,
        },
    )


@login_required
def financial_report(request):
    """Relatório financeiro do carmelo do usuário.

    Admins do Django (is_staff) veem o relatório GLOBAL de todos os carmelos
    juntos; os demais (manager/tesoureiro, com permissão see_total_money)
    veem apenas o do próprio carmelo.
    """
    # Staff (admin do Django) sempre pode ver o relatório global;
    # demais usuários precisam da permissão financeira do próprio carmelo.
    if not (request.user.is_staff or has_permission(request.user, "see_total_money")):
        raise PermissionDenied

    is_global = request.user.is_staff

    if is_global:
        summary = get_financial_summary(by_carmel=True)
        title = "Relatório Financeiro Global"
    else:
        carmel = request.user.carmel
        if not carmel:
            messages.error(
                request, "Nenhum carmelo vinculado ao seu usuário para gerar o relatório."
            )
            return redirect(reverse("home"))
        summary = get_financial_summary(carmel=carmel)
        title = f"Relatório Financeiro — {carmel.name}"

    return render(
        request,
        "contribution/financial_report.html",
        {"summary": summary, "title": title, "is_global": is_global},
    )


@login_required
@has_permission_decorator("list_contribute")
def contribution_member(request, slug):
    """Lista as contribuições de um membro e permite registrar novas."""
    carmel: Carmel = request.user.carmel

    if not carmel:
        messages.error(request, "Nenhum carmelo relacionado ao usuário logado.")
        return redirect(reverse("list_member"))

    member = get_object_or_404(Member, slug=slug, carmel=carmel)

    form = ContributionForm(member=member)
    months = month_empty(member)
    date_entry = member.entry_date
    contributions = paginate(
        Contribution.objects.filter(member=member).order_by("-date_pay"),
        request,
        per_page=10,
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
