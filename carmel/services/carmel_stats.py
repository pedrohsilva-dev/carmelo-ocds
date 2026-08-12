from datetime import date
from django.db.models import Count, Sum, Avg, Q

from contributions.models import Contribution
from members.models import Member

ROLE_LABELS = {
    "MN": "Responsável",
    "FN": "Tesoureiro",
    "NM": "Normal",
}


def get_carmel_statistics(carmel):
    """Retorna estatísticas importantes para o Carmelo."""
    today = date.today()
    current_year = today.year
    current_month = today.month

    member_queryset = Member.objects.filter(carmel=carmel)
    contribution_queryset = Contribution.objects.filter(member__carmel=carmel)

    # Estatísticas de membros
    total_members = member_queryset.count()
    active_members = member_queryset.filter(is_active=True).count()
    inactive_members = total_members - active_members
    roles_summary = (
        member_queryset.values("roles").annotate(count=Count("id")).order_by("roles")
    )
    roles_summary = [
        {
            "roles": item["roles"],
            "label": ROLE_LABELS.get(item["roles"], "Sem função"),
            "count": item["count"],
        }
        for item in roles_summary
    ]

    # Estatísticas de contribuições
    total_contributions = (
        contribution_queryset.aggregate(total=Sum("price"))["total"] or 0
    )
    average_contribution = contribution_queryset.aggregate(avg=Avg("price"))["avg"] or 0
    contributions_this_month = (
        contribution_queryset.filter(
            date_pay__year=current_year,
            date_pay__month=current_month,
        ).aggregate(total=Sum("price"))["total"]
        or 0
    )
    contributions_this_year = (
        contribution_queryset.filter(date_pay__year=current_year).aggregate(
            total=Sum("price")
        )["total"]
        or 0
    )

    # Totais mensais dos últimos 6 meses
    month_labels = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]

    # Totais mensais dos últimos 6 meses — UMA query com agregação condicional
    month_targets = []
    for offset in range(5, -1, -1):
        month = current_month - offset
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        month_targets.append((month, year))

    monthly_agg = contribution_queryset.aggregate(
        **{
            f"m{idx}_total": Sum(
                "price",
                filter=Q(
                    date_pay__year=target_year,
                    date_pay__month=target_month,
                ),
            )
            for idx, (target_month, target_year) in enumerate(month_targets)
        }
    )

    monthly_totals = [
        {
            "label": month_labels[month - 1],
            "year": year,
            "total": monthly_agg.get(f"m{idx}_total") or 0,
        }
        for idx, (month, year) in enumerate(month_targets)
    ]

    # Grupos de contribuição por membro
    contribution_by_member = (
        contribution_queryset.values("member__name")
        .annotate(total=Sum("price"), count=Count("id"))
        .order_by("-total")[:8]
    )

    # Membros com contribuição em atraso (mês atual não registrado)
    overdue_members = (
        member_queryset.annotate(
            latest_contribution=Sum(
                "contributions__price",
                filter=Q(
                    contributions__date_pay__year=current_year,
                    contributions__date_pay__month=current_month,
                ),
            )
        )
        .filter(~Q(latest_contribution__gt=0))
        .count()
    )

    chart_month_labels = [item["label"] for item in monthly_totals]
    chart_month_values = [float(item["total"]) for item in monthly_totals]
    chart_role_labels = [item["label"] for item in roles_summary]
    chart_role_values = [item["count"] for item in roles_summary]
    contribution_member_names = [
        item["member__name"] for item in contribution_by_member
    ]
    contribution_member_totals = [
        float(item["total"]) for item in contribution_by_member
    ]

    pending_members = 0
    paid_months_by_member = {}
    today = date.today()
    contributions = (
        contribution_queryset.filter(date_pay__lte=today)
        .values("member_id", "date_pay__year", "date_pay__month")
        .distinct()
    )
    for contribution in contributions:
        paid_months_by_member.setdefault(contribution["member_id"], set()).add(
            (contribution["date_pay__year"], contribution["date_pay__month"])
        )

    members = list(member_queryset.only("id", "entry_date"))
    for member in members:
        start_year = member.entry_date.year
        start_month = member.entry_date.month
        expected_months = 0
        year, month = start_year, start_month
        while (year, month) <= (today.year, today.month):
            expected_months += 1
            month += 1
            if month > 12:
                month = 1
                year += 1

        paid = len(paid_months_by_member.get(member.pk, set()))
        if expected_months > paid:
            pending_members += 1

    no_pending_members = total_members - pending_members

    return {
        "total_members": total_members,
        "active_members": active_members,
        "inactive_members": inactive_members,
        "roles_summary": roles_summary,
        "total_contributions": total_contributions,
        "average_contribution": average_contribution,
        "contributions_this_month": contributions_this_month,
        "contributions_this_year": contributions_this_year,
        "monthly_totals": monthly_totals,
        "chart_month_labels": chart_month_labels,
        "chart_month_values": chart_month_values,
        "chart_role_labels": chart_role_labels,
        "chart_role_values": chart_role_values,
        "contribution_by_member": list(contribution_by_member),
        "contribution_member_names": contribution_member_names,
        "contribution_member_totals": contribution_member_totals,
        "overdue_members": overdue_members,
        "pending_members": pending_members,
        "no_pending_members": no_pending_members,
        "pending_chart_labels": ["Pendentes", "Sem pendências"],
        "pending_chart_values": [pending_members, no_pending_members],
    }
