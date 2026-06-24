from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from votes.forms import VoteForm, VoteRegisterForm
from django.utils import timezone
from members.models import Member
from votes.models import Vote, VotesRegistration

from django.contrib import messages

from django.shortcuts import get_object_or_404, render

from rolepermissions.decorators import has_permission_decorator

# 'create_vote': True,
# 'read_vote': True,
# 'edit_vote': True,
# 'delete_vote': True,
# 'list_vote': True,


# Create your views here.
@login_required
@has_permission_decorator("create_vote")
def register_vote(request):
    user_current = request.POST.get("user_current")
    user = Member.objects.filter(slug=user_current).first()

    if request.method == "POST":
        form_vote = VoteForm(request.POST)

        if form_vote.is_valid():
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
        {"votes": votes, "user_current": user_current, "form_vote": form_vote},
    )


@login_required
@has_permission_decorator("list_vote")
def vote_member(request, user, id):
    votes = VotesRegistration.objects.select_related("votes_registration").all()

    return render(
        request,
        "votes/components_votes/option_vote_registration.html",
        {"votes": votes},
    )


@login_required
@has_permission_decorator("edit_vote")
def edit_vote_member(request, user, id):
    if request.method == "GET":
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
    form_update = VoteForm(request.POST)
    if form_update.is_valid():
        vote = Vote.objects.filter(id=id).first()

        if vote:
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
            "user_current": user_current,
        },
    )


@login_required
@has_permission_decorator("delete_vote")
def delete_vote(request, id: int):
    form_vote = VoteForm()
    user_current = request.POST.get("user_current")

    vote = Vote.objects.filter(id=id).first()

    if vote:
        vote.delete()

        messages.success(request, "Voto deletado")

        votes = Vote.objects.filter(member__slug=user_current).all()

    return render(
        request,
        "votes/components_votes/list_votes.html",
        {"votes": votes, "user_current": user_current, "form_vote": form_vote},
    )


@login_required
@has_permission_decorator("list_vote")
def votes_member(request, slug):
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

    form = VoteRegisterForm(request.POST)
    exists = VotesRegistration.objects.filter(name=form.data.get("name")).exists()

    if exists:
        messages.warning(request, "Voto Já cadastrado!")

    if form.is_valid() and not exists:
        messages.success(request, "Opção de Voto cadastrado com sucesso!")
        form.save()
        form = VoteRegisterForm(initial={})

    if not exists:
        votes_registration = VotesRegistration.objects.all()

    return render(
        request,
        "votes/components_votes/list_votes_registration.html",
        {"votes_registration": votes_registration, "form": form},
    )


@login_required
@has_permission_decorator("delete_votes_registration")
def delete_votes_registration(request, id):
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
