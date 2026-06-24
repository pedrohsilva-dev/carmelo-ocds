from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = "members"
    verbose_name = "Membros do Carmelo"

    def ready(self):
        import members.signals
