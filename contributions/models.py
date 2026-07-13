from datetime import date

from django.db import models

from base.models import TimeStampedModel
from members.models import Member
from django.core.exceptions import ValidationError

# Create your models here.


class Contribution(TimeStampedModel):

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor da Contribuição",
    )

    date_pay = models.DateField(verbose_name="Data do Pagamento")

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
                fields=["member", "date_pay"], name="unique_member_contribution_date"
            )
        ]

    def clean(self):

        if not self.member_id:  # type: ignore
            return

        exists = Contribution.objects.filter(
            member_id=self.member_id,  # type: ignore
            date_pay__year=self.date_pay.year,
            date_pay__month=self.date_pay.month,
        )

        if self.pk:
            exists = exists.exclude(pk=self.pk)

        if exists.exists():
            raise ValidationError("Já existe uma contribuição neste mês.")

    def __str__(self):
        return f"{self.member} - {self.price}"
