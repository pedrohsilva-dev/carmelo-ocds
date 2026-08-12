from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rolepermissions.decorators import has_permission_decorator

from carmel.forms import CarmelForm
from carmel.services.carmel_stats import get_carmel_statistics

# Create your views here.


def _is_admin(user):
    """Apenas staff/superuser (administradores do sistema) criam carmelos."""
    return bool(user.is_authenticated and (user.is_staff or user.is_superuser))


@login_required
def create_carmel(request):
    """Cria um novo carmelo — restrito a administradores do sistema."""
    if not _is_admin(request.user):
        messages.error(
            request,
            "Apenas administradores do sistema podem criar carmelos.",
        )
        return redirect("profile")

    form = CarmelForm()

    if request.method == "POST":
        form = CarmelForm(request.POST)
        if form.is_valid():
            carmel = form.save()
            messages.success(
                request,
                f"Carmelo '{carmel.name}' criado com sucesso!",
            )
            return redirect("carmel_profile")

    return render(request, "create_carmel.html", {"form": form})


@login_required
@has_permission_decorator("edit_carmel")
def edit_carmel(request):
    """Salva a edição das informações do carmelo (POST)."""
    user = request.user

    if not user or not user.carmel:
        messages.error(
            request,
            "Usuário incompleto para editar o carmelo. Entre em contato com o administrador do sistema.",
        )
        return redirect("/")

    if request.method != "POST":
        return redirect("carmel_profile")

    carmel = user.carmel
    form = CarmelForm(request.POST, instance=carmel)

    if form.is_valid():
        form.save()
        messages.success(request, "Carmelo atualizado com sucesso!")
    else:
        messages.error(request, "Corrija os erros do formulário.")

    return redirect("carmel_profile")


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

    # Estatísticas agregadas (uma única chamada de serviço)
    carmel_stats = get_carmel_statistics(carmel)

    # edit carmel (preenche o modal)
    form = CarmelForm(instance=carmel)

    context = {
        "carmel": carmel,
        "form": form,
        "is_admin": _is_admin(user),
        **carmel_stats,
    }

    return render(request, "carmel_profile.html", context)
