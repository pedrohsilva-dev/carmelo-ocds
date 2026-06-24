from rolepermissions.roles import AbstractUserRole


class NormalMember(AbstractUserRole):
    available_permissions = {"login": True, "home": True, "profile": True}


class FinanceMember(AbstractUserRole):
    available_permissions = {
        "login": True,
        "home": True,
        "profile": True,
        "see_total_money": True,
        "show_money": True,
        "carmel_dashboard": True,
        "list_members": True,
        # CONTROL CONTRIBUTION
        "create_Contribute": True,
        "read_contribute": True,
        "edit_contribute": True,
        "delete_contribute": True,
        "list_contribute": True,
    }


class ManagerMember(AbstractUserRole):
    available_permissions = {
        "login": True,
        "home": True,
        "profile": True,
        "carmel_dashboard": True,
        "view_carmel": True,
        "see_total_money": True,
        "show_money": True,
        # MEMBER
        "create_member": True,
        "read_member": True,
        "edit_member": True,
        "delete_member": True,
        "list_members": True,
        # VOTES
        "create_vote": True,
        "read_vote": True,
        "edit_vote": True,
        "delete_vote": True,
        "list_vote": True,
        # CONTRIBUTE
        "create_Contribute": True,
        "read_contribute": True,
        "edit_contribute": True,
        "delete_contribute": True,
        "list_contribute": True,
        # VOTES REGISTRATION
        "create_votes_registration": True,
        "read_votes_registration": True,
        "edit_votes_registration": True,
        "delete_votes_registration": True,
        "list_votes_registration": True,
    }
