from django.test import TestCase
from django.urls import reverse
from rolepermissions.checkers import has_role

from carmel.models import Carmel
from members.models import Member


class MemberTests(TestCase):

    def setUp(self):
        self.carmel = Carmel.objects.create(
            name="Carmelo Teste",
            description="Comunidade de teste",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
        )
        self.other_carmel = Carmel.objects.create(
            name="Carmelo Segundo",
            description="Outra comunidade",
            price_contribution_default="40.00",
            pay_day_contribution_default=5,
        )
        self.manager = Member.objects.create_user(
            email="manager@carmelo.org",
            name="Gestor Teste",
            password="SenhaForte123!",
            church="Paróquia São José",
            entry_date="2023-01-01",
            carmel=self.carmel,
            roles="MN",
        )
        self.normal = Member.objects.create_user(
            email="normal@carmelo.org",
            name="Membro Normal",
            password="SenhaForte123!",
            church="Paróquia São José",
            entry_date="2024-01-01",
            carmel=self.carmel,
            roles="NM",
        )

    # ==========================================================
    # ROLES / SIGNAL
    # ==========================================================

    def test_role_is_assigned_by_signal(self):
        self.assertTrue(has_role(self.manager, "manager_member"))
        self.assertTrue(has_role(self.normal, "normal_member"))

    def test_role_label_property(self):
        self.assertEqual(self.manager.role_label, "Responsavel")
        self.assertEqual(self.normal.role_label, "Normal")

    # ==========================================================
    # PERMISSIONS
    # ==========================================================

    def test_normal_member_cannot_access_member_list(self):
        self.client.login(identifier="normal@carmelo.org", password="SenhaForte123!")
        response = self.client.get(reverse("list_member"))
        self.assertEqual(response.status_code, 403)

    def test_manager_can_access_member_list(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        response = self.client.get(reverse("list_member"))
        self.assertEqual(response.status_code, 200)

    def test_manager_can_register_member(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        response = self.client.post(
            reverse("register_member"),
            {
                "name": "Novo Membro",
                "email": "novo@carmelo.org",
                "church": "Paróquia Santa Rita",
                "entry_date": "2025-01-01",
                "roles": "NM",
                "password": "SenhaForte123!",
                "password2": "SenhaForte123!",
            },
        )
        self.assertRedirects(response, reverse("list_member"))
        self.assertTrue(Member.objects.filter(email="novo@carmelo.org").exists())

    def test_manager_cannot_register_member_in_future_date(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        response = self.client.post(
            reverse("register_member"),
            {
                "name": "Futuro Membro",
                "email": "futuro@carmelo.org",
                "church": "Paróquia Santa Rita",
                "entry_date": "2099-01-01",
                "roles": "NM",
                "password": "SenhaForte123!",
                "password2": "SenhaForte123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Member.objects.filter(email="futuro@carmelo.org").exists())

    # ==========================================================
    # TRANSFER FLOW
    # ==========================================================

    def test_transfer_member_requires_permission(self):
        self.client.login(identifier="normal@carmelo.org", password="SenhaForte123!")
        response = self.client.get(
            reverse("transfer_member", kwargs={"id": self.normal.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_transfer_member_flow(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")

        response = self.client.get(
            reverse("transfer_member", kwargs={"id": self.normal.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carmelo Segundo")

        response = self.client.post(
            reverse("transfer_member", kwargs={"id": self.normal.id}),
            {"target_carmel": self.other_carmel.id},
        )
        self.assertRedirects(response, reverse("list_member"))

        self.normal.refresh_from_db()
        self.assertEqual(self.normal.carmel_id, self.other_carmel.id)

    def test_show_member_is_scoped_to_carmel(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")

        outsider = Member.objects.create_user(
            email="outsider@carmelo.org",
            name="Forasteiro",
            password="SenhaForte123!",
            church="Outra igreja",
            entry_date="2024-01-01",
            carmel=self.other_carmel,
            roles="NM",
        )

        response = self.client.get(
            reverse("show_member", kwargs={"slug": outsider.slug})
        )
        self.assertEqual(response.status_code, 404)

    # ==========================================================
    # UPDATE / DELETE
    # ==========================================================

    def test_update_member_flow(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        response = self.client.post(
            reverse("update_member", kwargs={"id": self.normal.id}),
            {
                "name": "Membro Renomeado",
                "email": "normal@carmelo.org",
                "church": "Paróquia Santa Luzia",
                "entry_date": "2024-01-01",
                "roles": "NM",
                "password": "",
                "password2": "",
            },
        )
        self.assertRedirects(response, reverse("list_member"))
        self.normal.refresh_from_db()
        self.assertEqual(self.normal.name, "Membro Renomeado")
        self.assertEqual(self.normal.church, "Paróquia Santa Luzia")

    def test_delete_member_removes_and_rerenders(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse("delete_member", kwargs={"id": self.normal.id})
        response = self.client.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Member.objects.filter(pk=self.normal.pk).exists())
        self.assertContains(response, "Não foi encontrado nenhum Membro")

    def test_normal_member_cannot_delete_member(self):
        self.client.login(identifier="normal@carmelo.org", password="SenhaForte123!")
        url = reverse("delete_member", kwargs={"id": self.normal.id})
        response = self.client.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Member.objects.filter(pk=self.normal.pk).exists())

    # ==========================================================
    # CSRF (regressão do hx-post) — mesmo padrão do bug de contribuições
    # ==========================================================

    def test_members_list_page_always_renders_csrf_input(self):
        """O token CSRF deve existir na página para o botão Deletar (hx-post)."""
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        response = self.client.get(reverse("list_member"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_delete_member_works_with_real_csrf(self):
        """Simula o navegador real: token CSRF extraído da página + POST."""
        import re

        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        client.login(identifier="manager@carmelo.org", password="SenhaForte123!")

        page = client.get(reverse("list_member"))
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page.content.decode())
        self.assertIsNotNone(match, "Token CSRF não encontrado na página")
        token = match.group(1)

        url = reverse("delete_member", kwargs={"id": self.normal.id})
        response = client.post(url, {}, HTTP_HX_REQUEST="true", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Member.objects.filter(pk=self.normal.pk).exists())
