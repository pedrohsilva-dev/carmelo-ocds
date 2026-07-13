from django.shortcuts import render


def home(request):
    """Renderiza a página inicial do sistema.

    Simples view que exibe a página home.
    """
    return render(request, "home.html")
