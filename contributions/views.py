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
