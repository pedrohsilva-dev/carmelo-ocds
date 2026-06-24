from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .forms import MemberForm, MemberChangeForm

from members.models import Member, Phone
from datetime import date

from django.contrib import messages

from rolepermissions.decorators import (
    has_role_decorator,
    has_role,
    has_permission_decorator,
)

# Create your views here.

# 'create_member': True,
# 'read_member': True,
# 'edit_member': True,
# 'delete_member': True,
# 'list_members': True,


# FUNCTIONS


def filter_member_object(id):
    return (
        Member.objects.filter(is_superuser=False, is_staff=False, is_active=True)
        .order_by("name")
        .all()
        .exclude(id=id)
    )


@login_required
@has_permission_decorator("create_member")
def register_member(request):
    form = MemberForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.clean_email()
            form.clean()
            member = form.save(commit=False)

            member.carmel = request.user.carmel

            member.save()

            return redirect("/members")
    return render(request, "members/register.html", {"form": form})


@login_required
@has_permission_decorator("list_members")
def members_aLL(request):
    members = filter_member_object(request.user.id)

    month = date.today().month

    return render(request, "members/list.html", {"members": members})


@login_required
@has_permission_decorator("list_members")
def filter_members(request):

    name_filter = request.POST.get("filter_name")

    if name_filter or date:
        members = filter_member_object(request.user.id).filter(
            name__icontains=name_filter
        )
    else:
        members = filter_member_object(request.user.id).all()

    return render(
        request, "members/components/list_filter_members.html", {"members": members}
    )


@login_required
@has_permission_decorator("read_member")
def show_member(request, slug):

    member = get_object_or_404(Member, slug=slug)

    phones = member.phones()
    location = member.location()

    return render(
        request,
        "members/show.html",
        {"member": member, "phones": phones, "location": location},
    )


@login_required
@has_permission_decorator("edit_member")
def update_member(request, id: int):
    member = get_object_or_404(Member, id=id)
    form = MemberChangeForm(instance=member)

    if request.method == "POST":
        form = MemberChangeForm(request.POST, instance=member)
        if form.is_valid():
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            if password and password2:
                user = form.save(commit=False)
                if password and password2 and password != password2:
                    messages.error(request, "Erro na troca de senha")
                    return redirect(reverse("list_member"))

                user.set_password(password)
                messages.success(request, "Atualizado com sucesso")
                user.save()
            else:
                form.save()

            return redirect(reverse("list_member"))

    return render(request, "members/update.html", {"form": form, "id": id})


@login_required
@has_permission_decorator("delete_member")
def delete_member(request, id: int):
    member = get_object_or_404(Member, id=id)
    member.delete()

    members = filter_member_object(request.user.id).all()

    return render(
        request, "members/components/list_filter_members.html", {"members": members}
    )
