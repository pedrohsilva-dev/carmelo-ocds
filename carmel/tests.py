from django.test import TestCase
from django.urls import reverse

from carmel.models import Carmel
from members.models import Member


class CreateCarmelTests(TestCase):
    """Somente administradores (staff/superuser) podem criar carmelos."""

    def setUp(self):
        self.carmel = Carmel.objects.create(
            name="Carmelo Base",
            description="Comunidade base",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
            diocese="Diocese de Itapetininga",
            city="Itapetininga",
        )
        self.password = "SenhaForte123!"
        self.normal = Member.objects.create_user(
            email="normal@carmelo.org",
            name="Membro Normal",
            password=self.password,
            church="Paróquia São José",
            entry_date="2024-01-01",
            carmel=self.carmel,
            roles="NM",
        )
        self.admin = Member.objects.create_user(
            email="admin@carmelo.org",
            name="Admin Sistema",
            password=self.password,
            church="Paróquia São José",
            entry_date="2024-01-01",
            carmel=self.carmel,
            roles="MN",
        )
        self.admin.is_staff = True
        self.admin.save()

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("create_carmel"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_normal_member_cannot_create_carmel(self):
        self.client.login(identifier="normal@carmelo.org", password=self.password)
        response = self.client.get(reverse("create_carmel"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("profile"), response.url)

        count_before = Carmel.objects.count()
        response = self.client.post(
            reverse("create_carmel"),
            {
                "name": "Carmelo Indevido",
                "description": "Não deveria ser criado",
                "city": "Itapetininga",
                "diocese": "Diocese de Itapetininga",
                "price_contribution_default": "50.00",
                "pay_day_contribution_default": 10,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("profile"), response.url)
        self.assertEqual(Carmel.objects.count(), count_before)

    def test_admin_can_open_create_page(self):
        self.client.login(identifier="admin@carmelo.org", password=self.password)
        response = self.client.get(reverse("create_carmel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Criar Carmelo")

    def test_admin_can_create_carmel(self):
        self.client.login(identifier="admin@carmelo.org", password=self.password)
        response = self.client.post(
            reverse("create_carmel"),
            {
                "name": "OCDS Itapetininga",
                "description": "Comunidade de Itapetininga",
                "city": "Itapetininga",
                "diocese": "Diocese de Itapetininga",
                "price_contribution_default": "60.00",
                "pay_day_contribution_default": 15,
            },
        )
        self.assertRedirects(response, reverse("carmel_profile"))

        carmel = Carmel.objects.get(name="OCDS Itapetininga")
        self.assertEqual(carmel.city, "Itapetininga")
        self.assertEqual(carmel.diocese, "Diocese de Itapetininga")
        self.assertEqual(float(carmel.price_contribution_default), 60.00)
        self.assertEqual(carmel.pay_day_contribution_default, 15)


class EditCarmelTests(TestCase):
    """Edição do carmelo inclui cidade e diocese."""

    def setUp(self):
        self.carmel = Carmel.objects.create(
            name="Carmelo Teste",
            description="Comunidade de teste",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
        )
        self.password = "SenhaForte123!"
        self.manager = Member.objects.create_user(
            email="gestor@carmelo.org",
            name="Gestor Carmelo",
            password=self.password,
            church="Paróquia São José",
            entry_date="2023-01-01",
            carmel=self.carmel,
            roles="MN",
        )

    def test_edit_updates_city_and_diocese(self):
        self.client.login(identifier="gestor@carmelo.org", password=self.password)
        response = self.client.post(
            reverse("edit_carmel"),
            {
                "name": "Carmelo Teste",
                "description": "Comunidade de teste atualizada",
                "city": "Itapetininga",
                "diocese": "Diocese de Itapetininga",
                "price_contribution_default": "55.00",
                "pay_day_contribution_default": 12,
            },
        )
        self.assertRedirects(response, reverse("carmel_profile"))

        self.carmel.refresh_from_db()
        self.assertEqual(self.carmel.city, "Itapetininga")
        self.assertEqual(self.carmel.diocese, "Diocese de Itapetininga")
        self.assertEqual(float(self.carmel.price_contribution_default), 55.00)
        self.assertEqual(self.carmel.pay_day_contribution_default, 12)
