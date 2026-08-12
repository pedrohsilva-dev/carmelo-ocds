from base.utils import paginate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render

from members.models import Address, Member, Phone

from .forms import AddressForm, PhoneForm

from rolepermissions.decorators import has_permission_decorator

# ==========================================================
# HELPERS
# ==========================================================


def get_contact_context(member, request=None):
    """
    Contexto compartilhado entre todos os componentes de contato.
    Telefones são paginados para telas grandes.
    """

    address = getattr(member, "address", None)
    phones = member.phones.all().order_by("name", "number")

    if request:
        phones = paginate(phones, request, per_page=12, page_param="phone_page")

    return {
        "member": member,
        "phones": phones,
        "address": address,
        "form_phone": PhoneForm(),
        "form_address": AddressForm(instance=address),
    }


# ==========================================================
# CONTACTS
# ==========================================================


@login_required
@has_permission_decorator("access_contacts")
def contacts(request, member_slug):
    member = get_object_or_404(Member, slug=member_slug, carmel=request.user.carmel)
    return render(
        request,
        "contacts/index.html",
        get_contact_context(member, request),
    )


# ==========================================================
# PHONE
# ==========================================================


@login_required
@has_permission_decorator("access_contacts")
def register_phone(request, member_slug):

    member = get_object_or_404(
        Member,
        slug=member_slug,
        carmel=request.user.carmel,
    )

    form = PhoneForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            phone = form.save(commit=False)

            exists = Phone.objects.filter(
                member=member,
                number=phone.number,
            ).exists()

            if exists:

                messages.error(
                    request,
                    "Este telefone já está cadastrado.",
                )

            else:

                with transaction.atomic():

                    phone.member = member
                    phone.save()

                messages.success(
                    request,
                    "Telefone cadastrado com sucesso.",
                )

    return render(
        request,
        "contacts/phones/index.html",
        get_contact_context(member, request),
    )


@login_required
@has_permission_decorator("access_contacts")
def delete_phone(request, id):

    phone = get_object_or_404(
        Phone,
        id=id,
        member__carmel=request.user.carmel,
    )

    member = phone.member

    with transaction.atomic():
        phone.delete()

    messages.success(
        request,
        "Telefone removido com sucesso.",
    )

    return render(
        request,
        "contacts/phones/index.html",
        get_contact_context(member, request),
    )


# ==========================================================
# ADDRESS
# ==========================================================


@login_required
@has_permission_decorator("access_contacts")
def register_address(request, member_slug):

    member = get_object_or_404(
        Member,
        slug=member_slug,
        carmel=request.user.carmel,
    )

    address = getattr(member, "address", None)

    form = AddressForm(
        request.POST or None,
        instance=address,
    )

    if request.method == "POST":

        if form.is_valid():

            with transaction.atomic():

                address = form.save(commit=False)
                address.member = member
                address.save()

            messages.success(
                request,
                "Endereço salvo com sucesso.",
            )

    return render(
        request,
        "contacts/address/index.html",
        get_contact_context(member, request),
    )


@login_required
@has_permission_decorator("access_contacts")
def edit_address(request, member_slug):

    member = get_object_or_404(
        Member,
        slug=member_slug,
        carmel=request.user.carmel,
    )

    address = get_object_or_404(
        Address,
        member=member,
    )

    form = AddressForm(
        request.POST or None,
        instance=address,
    )

    if request.method == "POST":

        if form.is_valid():

            with transaction.atomic():
                form.save()

            messages.success(
                request,
                "Endereço atualizado com sucesso.",
            )

    return render(
        request,
        "contacts/address/index.html",
        get_contact_context(member, request),
    )


@login_required
@has_permission_decorator("access_contacts")
def delete_address(request, member_slug):

    member = get_object_or_404(Member, slug=member_slug, carmel=request.user.carmel)
    address = getattr(member, "address", None)

    if address:
        with transaction.atomic():
            address.delete()

        member.refresh_from_db()  # ← invalida o cache da relação OneToOne

        messages.success(request, "Endereço removido com sucesso.")

    return render(
        request,
        "contacts/address/index.html",
        get_contact_context(member, request),
    )
