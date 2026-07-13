from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from base.models import TimeStampedModel

# Create your models here.


class Carmel(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=4000)
    # brand = models.ImageField('Logo do carmelo', upload_to="media")
    price_contribution_default = models.DecimalField(max_digits=1000, decimal_places=2)
    pay_day_contribution_default = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )

    class Meta:
        verbose_name = "Carmelo"
        verbose_name_plural = "Carmelos"

    def __str__(self) -> str:
        return self.name
