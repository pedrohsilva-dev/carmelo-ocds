from django.db import models

from members.models import Member, TimeStampedModel

# Create your models here.
TYPES_VOTES = (("DEF", "Definitivo"), ("TEMP", "Temporários"))


class VotesRegistration(models.Model):

    class Meta:
        verbose_name = "Registro do Voto e suas caracteristicas"
        verbose_name_plural = "Registro dos Votos e suas caracteristicas"

    name = models.CharField(max_length=40)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.name


class Vote(TimeStampedModel):

    votes_registration = models.ForeignKey(VotesRegistration, on_delete=models.CASCADE)

    date = models.DateTimeField(verbose_name="Data e Hora do Voto")

    type = models.CharField(
        max_length=4, choices=TYPES_VOTES, verbose_name="Grau do Voto"
    )

    year_duration = models.IntegerField(
        verbose_name="Quantos Anos dura esse voto", null=True, blank=True
    )

    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="Membro")

    class Meta:
        verbose_name = "Voto do Membro"
        verbose_name_plural = "Votos do Membro"

    def __str__(self):
        name = ""
        if self.votes_registration:
            name = self.votes_registration.name

        return name
