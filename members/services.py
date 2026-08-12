from datetime import date

from django.contrib import messages

from contributions.models import Contribution
from members.models import Member


def filter_carmel_members(carmel, exclude_id=None):
    """Membros de um carmelo (sem staff/superusuários), ordenados por nome.

    Útil para listas, filtros e para escolher membros para transferência.
    """
    qs = Member.objects.filter(
        is_superuser=False,
        is_staff=False,
        carmel=carmel,
    ).only("id", "name", "slug", "entry_date", "roles", "is_active")

    if exclude_id:
        qs = qs.exclude(id=exclude_id)

    return qs.order_by("name")


def get_member_pending_counts(members):
    """Retorna contagem de meses pendentes por membro.

    Recebe uma lista de membros e devolve:
        {member_pk: {"pending_count": int, "has_pending": bool}}
    """
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

        year, month = start_year, start_month
        while (year, month) <= (today.year, today.month):
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


def decorate_members_with_pending(member_list, pending_data=None):
    """Anexa `pending_count` e `has_pending` a cada membro da lista."""
    if pending_data is None:
        pending_data = get_member_pending_counts(member_list)

    for member in member_list:
        stats = pending_data.get(member.pk, {})
        setattr(member, "pending_count", stats.get("pending_count", 0))
        setattr(member, "has_pending", stats.get("has_pending", False))

    return member_list


def transfer_member_to_carmel(member, target_carmel):
    """Move um membro para outro carmelo (mesmo carmelo é no-op)."""
    if not target_carmel:
        raise ValueError("Carmealo de destino é obrigatório.")

    if member.carmel_id == target_carmel.id:
        return False

    member.carmel = target_carmel
    member.save(update_fields=["carmel", "updated_at"])

    return True


def available_carmels(exclude_carmel=None):
    """Carmelos disponíveis para transferência de um membro."""
    from carmel.models import Carmel

    qs = Carmel.objects.all().order_by("name")
    if exclude_carmel is not None:
        qs = qs.exclude(pk=exclude_carmel.pk)
    return qs
