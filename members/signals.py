from members.models import Member
from django.dispatch import receiver

from django.db.models.signals import post_save
from rolepermissions.roles import assign_role


@receiver(post_save, sender=Member)
def register_roles_member(sender, instance, created, **kwargs):
    if created:
        if instance.roles == "MN":
            assign_role(instance, "manager_member")
        elif instance.roles == "FN":
            assign_role(instance, "finance_member")
        elif instance.roles == "NM":
            assign_role(instance, "normal_member")
