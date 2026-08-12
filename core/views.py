from django.shortcuts import render

from carmel.models import Carmel


def home(request):
    """Renderiza a página inicial do sistema.

    Passa os dados do Carmelo (OCDS Itapetininga) para a landing page,
    com fallback quando ainda não houver registro cadastrado.
    """
    carmel = (
        Carmel.objects.filter(city__icontains="itapetininga")
        .order_by("id")
        .first()
        or Carmel.objects.order_by("id").first()
    )

    return render(request, "home.html", {"carmel": carmel})
