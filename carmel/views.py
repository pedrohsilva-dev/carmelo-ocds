from django.shortcuts import get_object_or_404, get_list_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from carmel.forms import CarmelForm
from carmel.models import Carmel
from contributions.models import Contribution
from members.models import Member

# Agregações do Django
from django.db.models.aggregates import Sum

# Create your views here.


@login_required
def edit_carmel(request):
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
def carmel_profile(request):
    user = request.user

    if not user:
        return redirect("/")

    carmel = get_object_or_404(Carmel, member=user)
    quantity = Member.objects.filter(
        carmel=carmel
    ).count()  # Mostra a quantidade de membros

    # Quero substituir essa soma por uma agregação
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
