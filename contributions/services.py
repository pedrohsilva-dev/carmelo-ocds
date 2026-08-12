from datetime import date

from django.db.models import Avg, Count, Q, Sum
from django.utils.dates import MONTHS

from contributions.models import Contribution


def month_empty(member):
    """Calcula os meses pagos, faltantes e a situação do membro.

    Considera o período entre a data de entrada do membro e hoje.
    """
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
    missing_months = sorted(expected_months - paid_months)

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


def get_financial_summary(carmel=None, months=12, by_carmel=False):
    """Resumo financeiro agregado de um carmelo (ou de todos, se carmel=None).

    Usa apenas agregações do Django (Sum/Count/Avg) — sem loops por registro.
    Se `by_carmel=True`, inclui também o total por carmelo (relatório global).
    """
    qs = Contribution.objects.select_related("carmel", "member")
    if carmel is not None:
        qs = qs.filter(carmel=carmel)

    today = date.today()
    year, month = today.year, today.month

    totals = qs.aggregate(
        total=Sum("price"),
        count=Count("id"),
        avg=Avg("price"),
        year_total=Sum("price", filter=Q(date_pay__year=year)),
        month_total=Sum(
            "price",
            filter=Q(date_pay__year=year, date_pay__month=month),
        ),
    )

    # Últimos N meses — uma única query com agregação condicional
    targets = []
    for offset in range(months - 1, -1, -1):
        target_month = month - offset
        target_year = year
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        targets.append((target_month, target_year))

    monthly_agg = qs.aggregate(
        **{
            f"t{i}": Sum(
                "price",
                filter=Q(date_pay__year=y, date_pay__month=m),
            )
            for i, (m, y) in enumerate(targets)
        }
    )

    monthly_totals = [
        {
            "month": target_month,
            "year": target_year,
            "label": MONTHS[target_month],
            "total": monthly_agg.get(f"t{i}") or 0,
        }
        for i, (target_month, target_year) in enumerate(targets)
    ]

    result = {
        "total": totals["total"] or 0,
        "count": totals["count"] or 0,
        "avg": totals["avg"] or 0,
        "year_total": totals["year_total"] or 0,
        "month_total": totals["month_total"] or 0,
        "monthly_totals": monthly_totals,
    }

    if by_carmel:
        # Relatório global: total por carmelo — agregação única, sem N+1
        by_carmel_agg = (
            Contribution.objects.values("carmel__name")
            .annotate(total=Sum("price"), count=Count("id"))
            .order_by("-total")
        )
        result["by_carmel"] = list(by_carmel_agg)
    else:
        # Relatório de um carmelo: ranking por membro
        by_member = (
            qs.values("member__name", "member__slug")
            .annotate(total=Sum("price"), count=Count("id"))
            .order_by("-total")
        )
        result["by_member"] = list(by_member)

    return result



