from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render

from members.models import Address, Member, Phone

from .forms import AddressForm, PhoneForm

# ==========================================================
# HELPERS
# ==========================================================


def get_contact_context(member):
    """
    Contexto compartilhado entre todos os componentes de contato.
    """

    address = getattr(member, "address", None)

    return {
        "member": member,
        "phones": member.phones.all().order_by("name", "number"),
        "address": address,
        "form_phone": PhoneForm(),
        "form_address": AddressForm(instance=address),
    }


# ==========================================================
# CONTACTS
# ==========================================================


@login_required
def contacts(request, member_slug):
    member = get_object_or_404(Member, slug=member_slug)
    return render(
        request,
        "contacts/index.html",
        get_contact_context(member),
    )


# ==========================================================
# PHONE
# ==========================================================


@login_required
def register_phone(request, member_slug):

    member = get_object_or_404(
        Member,
        slug=member_slug,
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
        get_contact_context(member),
    )


@login_required
def delete_phone(request, id):

    phone = get_object_or_404(
        Phone,
        id=id,
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
        get_contact_context(member),
    )


# ==========================================================
# ADDRESS
# ==========================================================


@login_required
def register_address(request, member_slug):

    member = get_object_or_404(
        Member,
        slug=member_slug,
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
        get_contact_context(member),
    )


@login_required
def edit_address(request, member_slug):

    member = get_object_or_404(
        Member,
        slug=member_slug,
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
        get_contact_context(member),
    )


@login_required
def delete_address(request, member_slug):

    member = get_object_or_404(Member, slug=member_slug)
    address = getattr(member, "address", None)

    if address:
        with transaction.atomic():
            address.delete()

        member.refresh_from_db()  # ← invalida o cache da relação OneToOne

        messages.success(request, "Endereço removido com sucesso.")

    return render(
        request,
        "contacts/address/index.html",
        get_contact_context(member),
    )
