from django.shortcuts import get_object_or_404, get_list_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from carmel.models import Carmel
from contributions.models import Contribution
from members.models import Member

# Agregações do Django
from django.db.models.aggregates import Sum

# Create your views here.


@login_required
def carmel_profile(request):
    user = request.user

    if not user:
        return redirect("/")

    carmel = get_object_or_404(Carmel, member=user)
    quantity = Member.objects.filter(
        carmel=carmel
    ).count()  # Mostra a quantidade de membros
    members = Member.objects.filter(carmel=carmel)  # Mostra a quantidade de membros

    sum = 0
    for member in members:
        contribution = Contribution.objects.filter(member=member).all()
        for contrib in contribution:
            sum += contrib.price

    # quero substituir essa soma por uma agregação
    total_contribuition = (
        Contribution.objects.filter(member__carmel=carmel).aggregate(Sum("price"))[
            "price__sum"
        ]
        or 0
    )
    print(total_contribuition)
    return render(
        request,
        "carmel_profile.html",
        {"carmel": carmel, "member_quantity": quantity, "total_contribuition": sum},
    )
