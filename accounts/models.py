from datetime import datetime, timedelta

from django.db import models
from members.models import Member
from secrets import token_urlsafe

# Create your models here.


class ResetPasswordAccess(models.Model):
    token = models.CharField("token de acesso", max_length=32, null=True, blank=True)
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    expired_at = models.DateTimeField(
        "Data e Hora de expiração do token", max_length=32, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        self.token = token_urlsafe(nbytes=16)
        self.expired_at = datetime.now() + timedelta(hours=1)

        super().save(*args, **kwargs)
