from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from contributions.models import Contribution
from members.models import Member, Phone, Address
from votes.models import Vote


class VotesInline(admin.TabularInline):
    model = Vote
    extra = 0
    fields = ("votes_registration", "date", "type", "year_duration")
    readonly_fields = ("date",)


class ContributionInline(admin.TabularInline):
    model = Contribution
    extra = 0
    fields = ("price", "date_pay", "carmel")


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 0


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    max_num = 1


class MemberAdminCreationForm(UserCreationForm):
    """Criação de membro no admin (email + nome + senha)."""

    class Meta(UserCreationForm.Meta):
        model = Member
        fields = ("email", "name")


class MemberAdminChangeForm(UserChangeForm):
    """Edição de membro no admin — mantém o campo de senha com o
    link "Trocar senha" do Django."""

    class Meta(UserChangeForm.Meta):
        model = Member
        fields = "__all__"


@admin.register(Member)
class MemberAdmin(UserAdmin):
    add_form = MemberAdminCreationForm
    form = MemberAdminChangeForm

    list_display = (
        "name",
        "email",
        "roles",
        "carmel",
        "is_active",
        "is_staff",
        "last_login",
    )
    list_display_links = ("name", "email")
    search_fields = ("email", "name")
    list_filter = ("roles", "is_active", "is_staff", "carmel")
    ordering = ("name",)

    inlines = [
        PhoneInline,
        AddressInline,
        ContributionInline,
        VotesInline,
    ]

    fieldsets = (
        ("Autenticação", {
            "fields": ("email", "name", "password")
        }),
        ("Informações", {
            "fields": (
                "church",
                "entry_date",
                "carmel",
                "roles",
                "slug",
            )
        }),
        ("Permissões", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "name",
                "password1",
                "password2",
                "is_staff",
                "is_active",
            ),
        }),
    )

    readonly_fields = ("last_login",)

    def get_inline_instances(self, request, obj=None):
        # Inlines apenas na edição (não no "adicionar" sem objeto)
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


admin.site.register(Phone)
admin.site.register(Address)
