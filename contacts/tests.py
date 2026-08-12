from django.test import TestCase
from django.urls import reverse

from carmel.models import Carmel
from members.models import Address, Member, Phone


class ContactsCrudTests(TestCase):
    """Valida o CRUD de telefones e endereços no app de contatos."""

    def setUp(self):
        self.carmel = Carmel.objects.create(
            name="Carmelo Teste",
            description="Comunidade de teste",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
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
        self.member = Member.objects.create_user(
            email="maria@carmelo.org",
            name="Maria Oliveira",
            password="SenhaForte123!",
            church="Paróquia São José",
            entry_date="2024-06-01",
            carmel=self.carmel,
            roles="NM",
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")

    def _index_url(self):
        return reverse("contacts:index", kwargs={"member_slug": self.member.slug})

    # ==========================================================
    # PHONE
    # ==========================================================

    def test_register_phone(self):
        url = reverse(
            "contacts:register_phone", kwargs={"member_slug": self.member.slug}
        )
        response = self.client.post(
            url,
            {"name": "Casa", "number": "(15) 99999-0001"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Phone.objects.filter(member=self.member, number="(15) 99999-0001").exists()
        )

    def test_duplicate_phone_rejected(self):
        Phone.objects.create(member=self.member, name="Casa", number="(15) 99999-0002")
        url = reverse(
            "contacts:register_phone", kwargs={"member_slug": self.member.slug}
        )
        response = self.client.post(
            url,
            {"name": "Casa", "number": "(15) 99999-0002"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Phone.objects.filter(member=self.member, number="(15) 99999-0002").count(),
            1,
        )

    def test_delete_phone(self):
        phone = Phone.objects.create(
            member=self.member, name="Casa", number="(15) 99999-0003"
        )
        url = reverse("contacts:delete_phone", kwargs={"id": phone.id})
        response = self.client.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Phone.objects.filter(pk=phone.pk).exists())

    # ==========================================================
    # ADDRESS
    # ==========================================================

    def _address_payload(self, **overrides):
        payload = {
            "street": "Rua das Flores",
            "number": "123",
            "neighborhood": "Centro",
            "city": "Itapetininga",
            "state": "SP",
            "zipcode": "18200-000",
        }
        payload.update(overrides)
        return payload

    def test_register_address(self):
        url = reverse(
            "contacts:register_address", kwargs={"member_slug": self.member.slug}
        )
        response = self.client.post(url, self._address_payload(), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Address.objects.filter(member=self.member).exists())

    def test_edit_address(self):
        Address.objects.create(member=self.member, street="Rua Velha", number="1")
        url = reverse(
            "contacts:edit_address", kwargs={"member_slug": self.member.slug}
        )
        response = self.client.post(
            url, self._address_payload(street="Rua Nova"), HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertEqual(self.member.address.street, "Rua Nova")

    def test_delete_address(self):
        Address.objects.create(member=self.member, street="Rua Velha", number="1")
        url = reverse(
            "contacts:delete_address", kwargs={"member_slug": self.member.slug}
        )
        response = self.client.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Address.objects.filter(member=self.member).exists())

    # ==========================================================
    # SCENING: member de outro carmelo fica de fora
    # ==========================================================

    def test_phone_of_other_carmel_cannot_be_deleted(self):
        other = Carmel.objects.create(
            name="Carmelo Outro",
            description="Outra comunidade",
            price_contribution_default="40.00",
            pay_day_contribution_default=5,
        )
        outsider = Member.objects.create_user(
            email="outsider@carmelo.org",
            name="Forasteiro",
            password="SenhaForte123!",
            church="Outra igreja",
            entry_date="2024-01-01",
            carmel=other,
            roles="NM",
        )
        phone = Phone.objects.create(
            member=outsider, name="Casa", number="(15) 98888-0000"
        )
        url = reverse("contacts:delete_phone", kwargs={"id": phone.id})
        response = self.client.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Phone.objects.filter(pk=phone.pk).exists())
