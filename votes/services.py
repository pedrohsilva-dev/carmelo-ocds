from votes.models import Vote, VotesRegistration


def get_member_votes(member):
    """Votos de um membro, com o registro de voto carregado."""
    return (
        Vote.objects.filter(member=member)
        .select_related("votes_registration")
        .order_by("-date")
    )


def get_votes_registration():
    """Catálogo de registros de voto disponíveis no sistema."""
    return VotesRegistration.objects.all().order_by("name")


