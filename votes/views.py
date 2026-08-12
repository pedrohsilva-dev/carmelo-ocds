from base.utils import paginate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, render
from rolepermissions.decorators import has_permission_decorator

from members.models import Member
from votes.forms import VoteForm, VoteRegisterForm
from votes.models import Vote, VotesRegistration
from votes.services import get_member_votes, get_votes_registration

# 'create_vote': True,
# 'read_vote': True,
# 'edit_vote': True,
# 'delete_vote': True,
# 'list_vote': True,


# Create your views here.
@login_required
@has_permission_decorator("create_vote")
def register_vote(request):
    """Registra um novo voto para um membro (valida duplicidade)."""
    form_vote = VoteForm()

    user_current = request.POST.get("user_current")
    user = None
    if user_current:
        user = Member.objects.filter(
            slug=user_current, carmel=request.user.carmel
        ).first()

    if request.method == "POST":
        form_vote = VoteForm(request.POST)

        if form_vote.is_valid():
            if user is None:
                messages.error(request, "Membro não encontrado.")
            else:
                vote_exists = Vote.objects.filter(
                    member=user,
                    votes_registration=form_vote.cleaned_data["votes_registration"],
                ).exists()

                if not vote_exists:
                    vote = form_vote.save(commit=False)
                    vote.member = user
                    vote.save()
                    form_vote = VoteForm()
                    messages.success(request, "Voto salvo com sucesso!")
                else:
                    messages.error(request, "O membro já possui esse voto!")

    votes = paginate(get_member_votes(user), request, per_page=10) if user else []

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
    """Lista as opções de voto disponíveis para associação (HTMX)."""
    get_object_or_404(Member, slug=user, carmel=request.user.carmel)
    votes = get_votes_registration()

    return render(
        request,
        "votes/components_votes/option_vote_registration.html",
        {"votes": votes},
    )


@login_required
@has_permission_decorator("edit_vote")
def edit_vote_member(request, user, id):
    """Carrega o formulário de edição de um voto específico (HTMX)."""
    form = None

    if request.method == "GET":
        vote = get_object_or_404(
            Vote, id=id, member__slug=user, member__carmel=request.user.carmel
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
    """Atualiza um voto existente (HTMX)."""
    vote = get_object_or_404(Vote, id=id, member__carmel=request.user.carmel)

    form_update = VoteForm(request.POST, instance=vote)
    if form_update.is_valid():
        votes_registration = form_update.cleaned_data["votes_registration"]

        # Impede que o membro fique com o mesmo voto duplicado
        duplicate = Vote.objects.filter(
            member=vote.member, votes_registration=votes_registration
        ).exclude(pk=vote.pk)

        if duplicate.exists():
            messages.error(request, "O membro já possui esse voto!")
        else:
            form_update.save()
            messages.success(request, "Voto atualizado com sucesso!")

    user_current = request.POST.get("user_current", vote.member.slug)
    votes = paginate(get_member_votes(vote.member), request, per_page=10)

    return render(
        request,
        "votes/components_votes/list_votes.html",
        {
            "votes": votes,
            "vote_id": id,
            "form": VoteForm(),
            "form_update": form_update if form_update.errors else None,
            "user_current": user_current,
        },
    )


@login_required
@has_permission_decorator("delete_vote")
def delete_vote(request, id: int):
    """Deleta um voto de um membro (HTMX)."""
    form_vote = VoteForm()
    vote = get_object_or_404(Vote, id=id, member__carmel=request.user.carmel)
    member = vote.member
    user_current = request.POST.get("user_current", member.slug)

    vote.delete()
    messages.success(request, "Voto deletado.")

    votes = paginate(get_member_votes(member), request, per_page=10)

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
    """Lista todos os votos de um membro específico."""
    member = get_object_or_404(Member, slug=slug, carmel=request.user.carmel)
    votes = paginate(get_member_votes(member), request, per_page=10)
    form_vote = VoteForm()

    return render(
        request,
        "votes/list.html",
        {"votes": votes, "form_vote": form_vote, "user_current": slug},
    )


# ==========================================================
# REGISTROS DE VOTO (catálogo)
# ==========================================================


@login_required
@has_permission_decorator("list_votes_registration")
def votes_registration(request):
    """Lista as opções de voto disponíveis no sistema."""
    form = VoteRegisterForm()
    votes_registration = paginate(get_votes_registration(), request, per_page=12)

    return render(
        request,
        "votes/votes_registration.html",
        {"form": form, "votes_registration": votes_registration},
    )


@login_required
@has_permission_decorator("create_votes_registration")
def register_votes_registration(request):
    """Registra uma nova opção de voto (sem duplicatas)."""
    form = VoteRegisterForm(request.POST)
    votes_registration = paginate(get_votes_registration(), request, per_page=12)

    if request.method == "POST" and form.is_valid():
        name = form.cleaned_data["name"]
        exists = VotesRegistration.objects.filter(name__iexact=name).exists()

        if exists:
            messages.warning(request, "Voto já cadastrado!")
        else:
            form.save()
            messages.success(request, "Opção de voto cadastrada com sucesso!")
            form = VoteRegisterForm()
            votes_registration = paginate(get_votes_registration(), request, per_page=12)

    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {"votes_registration": votes_registration, "form": form},
    )


@login_required
@has_permission_decorator("edit_votes_registration")
def edit_vote_registration(request, id):
    """Carrega o formulário de edição de uma opção de voto (HTMX)."""
    form = None

    if request.method == "GET":
        vote = get_object_or_404(VotesRegistration, id=id)
        form = VoteRegisterForm(instance=vote)

    return render(
        request,
        "votes/components_votes/form_edit_vote_registration.html",
        {"form_update": form, "vote_id": id},
    )


@login_required
@has_permission_decorator("edit_votes_registration")
def update_vote_registration(request, id):
    """Atualiza uma opção de voto existente (HTMX)."""
    vote_registration = get_object_or_404(VotesRegistration, id=id)

    form_update = VoteRegisterForm(request.POST, instance=vote_registration)
    if form_update.is_valid():
        form_update.save()
        messages.success(request, "Registro de voto atualizado com sucesso!")

    votes_registration = paginate(get_votes_registration(), request, per_page=12)

    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {
            "votes_registration": votes_registration,
            "form": VoteRegisterForm(),
            "form_update": form_update if form_update.errors else None,
        },
    )


@login_required
@has_permission_decorator("delete_votes_registration")
def delete_votes_registration(request, id):
    """Deleta uma opção de voto do sistema (HTMX)."""
    vote_registration = get_object_or_404(VotesRegistration, id=id)

    try:
        vote_registration.delete()
        messages.success(request, "Nome do voto deletado com sucesso.")
    except ProtectedError:
        messages.error(
            request, "Não foi possível deletar: este voto está em uso por membros."
        )

    votes_registration = paginate(get_votes_registration(), request, per_page=12)

    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {
            "votes_registration": votes_registration,
            "form": VoteRegisterForm(),
        },
    )
