from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from rolepermissions.decorators import has_permission_decorator

from members.models import Member
from votes.forms import VoteForm, VoteRegisterForm
from votes.models import Vote, VotesRegistration

# 'create_vote': True,
# 'read_vote': True,
# 'edit_vote': True,
# 'delete_vote': True,
# 'list_vote': True,


# Create your views here.
@login_required
@has_permission_decorator("create_vote")
def register_vote(request):
    """Registra um novo voto para um membro.

    Valida se o membro já possui esse voto; se não, cria o registro.
    """
    user_current = request.POST.get("user_current")
    user = Member.objects.filter(slug=user_current).first()

    if request.method == "POST":
        form_vote = VoteForm(request.POST)

        if form_vote.is_valid():
            # MANUTENÇÃO: Usar .exists() em vez de .exists() para apenas verificar existência
            vote_exists = Vote.objects.filter(
                member=user,
                votes_registration__name=form_vote.cleaned_data.get(
                    "votes_registration"
                ),
            ).exists()
            if not vote_exists:
                vote = form_vote.save(commit=False)
                vote.member = user
                vote.save()
                form_vote = VoteForm()

                messages.success(request, "Voto Salvo com sucesso! ")
            else:
                messages.error(request, "O membro já possui esse voto!")

    votes = Vote.objects.filter(member=user).select_related("votes_registration").all()

    return render(
        request,
        "votes/components_votes/list_votes.html",
        {
            "votes": votes,
            "user_current": user_current,
            "form_vote": form_vote,
        },
    )


@login_required
@has_permission_decorator("list_vote")
def vote_member(request, user, id):
    """Lista todas as opções de voto disponíveis para seleção.

    Renderiza as opções de voto para associar a um membro.
    """
    # MANUTENÇÃO: Parâmetros 'user' e 'id' não são utilizados
    votes = VotesRegistration.objects.select_related("votes_registration").all()

    return render(
        request,
        "votes/components_votes/option_vote_registration.html",
        {"votes": votes},
    )


@login_required
@has_permission_decorator("edit_vote")
def edit_vote_member(request, user, id):
    """Carrega o formulário de edição de um voto específico.

    Renderiza o formulário preenchido com os dados do voto.
    """
    if request.method == "GET":
        # MANUTENÇÃO: Usar get_object_or_404 em vez de .first() para melhor tratamento de erro
        vote = (
            Vote.objects.filter(member__slug=user, id=id)
            .select_related("votes_registration")
            .first()
        )
        form = VoteForm(instance=vote)

    return render(
        request,
        "votes/components_votes/form_edit_vote_member.html",
        {"form_update": form, "vote_id": id, "user_current": user},
    )


@login_required
@has_permission_decorator("edit_vote")
def update_vote_member(request, id):
    """Atualiza um voto existente com novos dados.

    Processa a submissão do formulário e atualiza o voto no banco.
    """
    form_update = VoteForm(request.POST)
    if form_update.is_valid():
        vote = Vote.objects.filter(id=id).first()

        if vote:
            # MANUTENÇÃO: Refatorar para usar form.save()
            vote.date = form_update.cleaned_data.get("date")  # type: ignore
            vote.type = form_update.cleaned_data.get("type")  # type: ignore
            vote.votes_registration_id = form_update.cleaned_data.get("votes_registration")  # type: ignore
            if form_update.cleaned_data.get("type") == "TEMP":
                vote.year_duration = form_update.cleaned_data.get("year_duration")

            vote.save()

            form_update = None

            messages.success(request, "Voto atualizado com sucesso! ")

    # atualizando a lista de votos do membro
    user_current = request.POST.get("user_current")
    votes = (
        Vote.objects.select_related("votes_registration")
        .filter(member__slug=user_current)
        .all()
    )
    # renderizando a lista de votos do membro atualizado
    return render(
        request,
        "votes/components_votes/list_votes.html",
        {
            "votes": votes,
            "vote_id": id,
            "form_update": form_update,
            "form": VoteForm(),
            "user_current": user_current,
        },
    )


@login_required
@has_permission_decorator("delete_vote")
def delete_vote(request, id: int):
    """Deleta um voto de um membro.

    Remove o voto e renderiza a lista de votos atualizada.
    """
    form_vote = VoteForm()
    user_current = request.POST.get("user_current")

    # MANUTENÇÃO: Usar get_object_or_404 em vez de .first()
    vote = Vote.objects.filter(id=id).first()

    if vote:
        vote.delete()

        messages.success(request, "Voto deletado")

        votes = Vote.objects.filter(member__slug=user_current).all()

    return render(
        request,
        "votes/components_votes/list_votes.html",
        {
            "votes": votes,
            "user_current": user_current,
            "form_vote": form_vote,
        },
    )


@login_required
@has_permission_decorator("list_vote")
def votes_member(request, slug):
    """Lista todos os votos de um membro específico.

    Exibe o histórico de votos do membro com opção de adicionar novos.
    """
    votes = (
        Vote.objects.filter(member__slug=slug)
        .prefetch_related("votes_registration")
        .all()
    )
    form_vote = VoteForm()

    return render(
        request,
        "votes/list.html",
        {"votes": votes, "form_vote": form_vote, "user_current": slug},
    )


# registration


# 'create_votes_registration': True,
# 'read_votes_registration': True,
# 'edit_votes_registration': True,
# 'delete_votes_registration': True,
# 'list_votes_registration': True,
@login_required
@has_permission_decorator("list_votes_registration")
def votes_registration(request):
    """Lista todas as opções de voto disponíveis no sistema.

    Exibe as opções registradas e permite criar novas.
    """
    form = VoteRegisterForm()
    votes_registration = VotesRegistration.objects.all()

    return render(
        request,
        "votes/votes_registration.html",
        {"form": form, "votes_registration": votes_registration},
    )


@login_required
@has_permission_decorator("create_votes_registration")
def register_votes_registration(request):
    """Registra uma nova opção de voto no sistema.

    Valida se não existe duplicata e salva o novo tipo de voto.
    """
    form = VoteRegisterForm(request.POST)
    # MANUTENÇÃO: Usar form.data.get() pode falhar - melhor usar form.cleaned_data após validar
    exists = VotesRegistration.objects.filter(name=form.data.get("name")).exists()

    if exists:
        messages.warning(request, "Voto Já cadastrado!")

    if form.is_valid() and not exists:
        messages.success(request, "Opção de Voto cadastrado com sucesso!")
        form.save()
        form = VoteRegisterForm(initial={})

    # MANUTENÇÃO: Lógica confusa - sempre executa se not exists, mesmo se form não foi válido
    if not exists:
        votes_registration = VotesRegistration.objects.all()

    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {"votes_registration": votes_registration, "form": form},
    )


@login_required
@has_permission_decorator("edit_vote_registration")
def edit_vote_registration(request, id):
    """Carrega o formulário de edição de uma opção de voto.

    Renderiza o formulário preenchido com os dados da opção.
    """
    if request.method == "GET":
        # MANUTENÇÃO: Usar get_object_or_404 para melhor tratamento de erro
        vote = VotesRegistration.objects.get(id=id)
        form = VoteRegisterForm(instance=vote)

    return render(
        request,
        "votes/components_votes/form_edit_vote_registration.html",
        {"form_update": form, "vote_id": id},
    )


@login_required
@has_permission_decorator("edit_votes_registration")
def update_vote_registration(request, id):
    """Atualiza uma opção de voto existente.

    Processa a submissão do formulário e atualiza os dados da opção.
    """
    form_update = VoteRegisterForm(request.POST)
    if form_update.is_valid():
        # MANUTENÇÃO: Usar get_object_or_404 e form.save() para simplificar
        vote_registration = VotesRegistration.objects.filter(id=id).first()

        if vote_registration:
            vote_registration.name = form_update.cleaned_data.get("name")  # type: ignore
            vote_registration.description = form_update.cleaned_data.get("description")  # type: ignore
            vote_registration.save()

            form_update = None

            messages.success(request, "Registro de voto atualizado com sucesso! ")

    # atualizando a lista de registros de votos
    votes_registration = VotesRegistration.objects.all()
    # renderizando a lista de registros de votos atualizada
    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {
            "votes_registration": votes_registration,
            "form_update": form_update,
            "form": VoteRegisterForm(),
        },
    )


@login_required
@has_permission_decorator("delete_votes_registration")
def delete_votes_registration(request, id):
    """Deleta uma opção de voto do sistema.

    Remove o tipo de voto e renderiza a lista atualizada.
    """
    # MANUTENÇÃO: Validar se a deleção foi bem-sucedida de forma melhor
    is_votes_registration_deleted = get_object_or_404(
        VotesRegistration, id=id
    ).delete()[0]
    form = VoteRegisterForm()

    if is_votes_registration_deleted == 1:
        messages.success(request, "Nome do Voto Deletado com Sucesso")
    else:
        messages.error(request, "Erro ao Deletar Nome do Voto")

    votes_registration = VotesRegistration.objects.all()

    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {
            "votes_registration": votes_registration,
            "form": form,
        },
    )
