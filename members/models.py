from datetime import date
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from base.models import TimeStampedModel
from carmel.models import Carmel

from django.core.validators import validate_email

# =========================
# CONSTANTES
# =========================

ROLES_CARMEL = (
    (
        "MN",
        "Responsavel",
    ),  # ver Membros + Finanças + Registrar membros, passar titulo de responsavel
    ("FN", "Tesoreiro"),  # ver Finanças, passar titulo de responsavel
    ("NM", "Normal"),
)


# =========================
# MANAGER
# =========================


class MemberManager(BaseUserManager):

    def create_user(self, email, name, password=None, password2=None):
        if not email:
            raise ValueError("Email é obrigatório")

        if password != password2:
            raise ValueError("As senhas não coincidem")

        email = self.normalize_email(email)

        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password, password)

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.save(using=self._db)
        return user


# =========================
# MODELS AUXILIARES
# =========================


class Address(models.Model):

    street = models.CharField(max_length=80, verbose_name="Rua")

    number = models.CharField(max_length=10, verbose_name="Número")

    neighborhood = models.CharField(max_length=50, verbose_name="Bairro")

    city = models.CharField(max_length=50, verbose_name="Cidade")

    state = models.CharField(max_length=2, verbose_name="Estado")

    zipcode = models.CharField(max_length=10, verbose_name="CEP")

    member = models.OneToOneField(
        "Member",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="location",
    )

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.street}, {self.neighborhood}-{self.number}, {self.city}/{self.state} ({self.zipcode})"


class Phone(models.Model):

    name = models.CharField(max_length=40, blank=True, verbose_name="Descrição")

    number = models.CharField(max_length=15, verbose_name="Número")

    member = models.ForeignKey(
        "Member", on_delete=models.CASCADE, related_name="phones", blank=True, null=True
    )

    class Meta:
        verbose_name = "Telefone"
        verbose_name_plural = "Telefones"

    def __str__(self):
        return self.number


# =========================
# USER MODEL
# =========================


class Member(AbstractBaseUser, PermissionsMixin, TimeStampedModel):

    username = None

    name = models.CharField(max_length=100, verbose_name="Nome do Membro", unique=True)

    email = models.EmailField(unique=True, validators=[validate_email])

    church = models.CharField(
        max_length=100,
        verbose_name="Igreja que Participa",
        default="",
    )

    entry_date = models.DateField(
        verbose_name="Data de Entrada",
    )

    carmel = models.ForeignKey(
        Carmel,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="members",
        db_index=True,
    )

    roles = models.CharField(
        max_length=2,
        choices=ROLES_CARMEL,
        default="NM",
        verbose_name="Função no Carmelo",
    )

    slug = models.SlugField(unique=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MemberManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = date.today()

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Generate a unique slug using UUID
            while Member.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # def phones(self):
    #     return Phone.objects.filter(member=self).all()

    # def location(self):
    #     return Address.objects.filter(member=self).first()
