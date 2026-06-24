from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from base.models import TimeStampedModel

# Create your models here.


class Carmel(TimeStampedModel):
    name = models.CharField()
    description = models.TextField(max_length=255)
    # brand = models.ImageField('Logo do carmelo', upload_to="media")
    price_contribution_default = models.DecimalField(max_digits=1000, decimal_places=2)
    pay_day_contribution_default = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )

    def __str__(self) -> str:
        return self.name
