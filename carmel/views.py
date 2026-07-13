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
