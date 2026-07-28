from datetime import date

from django.core.exceptions import ValidationError
from django.db import models

from base.models import TimeStampedModel
from members.models import Member


class Contribution(TimeStampedModel):

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor da Contribuição",
    )

    date_pay = models.DateField(verbose_name="Data do Pagamento")

    carmel = models.ForeignKey(
        "carmel.Carmel",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="contributions",
        verbose_name="Membro",
    )

    class Meta:
        verbose_name = "Contribuição"
        verbose_name_plural = "Contribuições"

        constraints = [
            models.UniqueConstraint(
                fields=["member", "date_pay"],
                name="unique_member_contribution_date",
            )
        ]

    def clean(self):
        super().clean()

        if not self.member_id or not self.date_pay:
            return

        # Verifica se já existe contribuição no mesmo mês
        exists = (
            Contribution.objects.filter(
                member_id=self.member_id,
                date_pay__year=self.date_pay.year,
                date_pay__month=self.date_pay.month,
            )
            .exclude(pk=self.pk)
            .exists()
        )

        if exists:
            raise ValidationError(
                {
                    "date_pay": (
                        "Este membro já possui uma contribuição "
                        "registrada neste mês."
                    )
                }
            )

    def __str__(self):
        return f"{self.member} - {self.price}"
