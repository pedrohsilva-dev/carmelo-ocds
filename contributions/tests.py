from datetime import date

from django.test import TestCase
from django.urls import reverse

from carmel.models import Carmel
from contributions.forms import ContributionForm
from contributions.models import Contribution
from contributions.services import month_empty
from members.models import Member


class ContributionTests(TestCase):

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

    # ==========================================================
    # FORM VALIDATIONS
    # ==========================================================

    def test_price_must_be_positive(self):
        form = ContributionForm(
            {"date_pay": "2024-07-10", "price": "-5"}, member=self.member
        )
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_price_must_not_exceed_limit(self):
        form = ContributionForm(
            {"date_pay": "2024-07-10", "price": "999999999"}, member=self.member
        )
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_future_date_rejected(self):
        future = date.today().replace(year=date.today().year + 1)
        form = ContributionForm({"date_pay": future, "price": "50"}, member=self.member)
        self.assertFalse(form.is_valid())
        self.assertIn("date_pay", form.errors)

    def test_date_before_entry_rejected(self):
        form = ContributionForm(
            {"date_pay": "2024-01-01", "price": "50"}, member=self.member
        )
        self.assertFalse(form.is_valid())
        self.assertIn("date_pay", form.errors)

    def test_valid_form(self):
        form = ContributionForm(
            {"date_pay": "2024-07-10", "price": "50.00"}, member=self.member
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_blank_price_falls_back_to_carmel_default(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse("register_contribution", kwargs={"user": self.member.slug})
        response = self.client.post(
            url, {"date_pay": "2024-07-10", "price": ""}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        contrib = Contribution.objects.get(member=self.member, date_pay="2024-07-10")
        self.assertEqual(float(contrib.price), float(self.carmel.price_contribution_default))

    # ==========================================================
    # ONE CONTRIBUTION PER MONTH (model constraint)
    # ==========================================================

    def test_duplicate_month_rejected_by_model(self):
        from django.core.exceptions import ValidationError

        first = Contribution(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        first.full_clean()
        first.save()

        duplicate = Contribution(
            price="60.00",
            date_pay="2024-07-20",
            carmel=self.carmel,
            member=self.member,
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    # ==========================================================
    # MONTH_EMPTY SERVICE
    # ==========================================================

    def test_month_empty_counts(self):
        result = month_empty(self.member)
        self.assertGreater(result["count_missing"], 0)
        self.assertEqual(result["count_paid"], 0)

    # ==========================================================
    # VIEW: register contribution as manager
    # ==========================================================

    def test_register_contribution_view(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse("register_contribution", kwargs={"user": self.member.slug})
        response = self.client.post(
            url,
            {
                "date_pay": "2024-07-10",
                "price": "50.00",
                "csrfmiddlewaretoken": "x",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Contribution.objects.filter(member=self.member, date_pay="2024-07-10").exists()
        )

    def test_register_contribution_requires_permission(self):
        # Membro normal não pode registrar contribuições
        self.client.login(identifier="maria@carmelo.org", password="SenhaForte123!")
        url = reverse("register_contribution", kwargs={"user": self.member.slug})
        response = self.client.post(url, {"date_pay": "2024-07-10", "price": "50"})
        self.assertEqual(response.status_code, 403)

    # ==========================================================
    # VIEW: delete contribution
    # ==========================================================

    def test_delete_contribution_removes_and_rerenders(self):
        contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse(
            "delete_contribution",
            kwargs={"user": self.member.slug, "id": contrib.id},
        )
        response = self.client.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contribution.objects.filter(pk=contrib.pk).exists())
        self.assertContains(response, "Pagamentos Feitos")

    def test_delete_contribution_requires_permission(self):
        contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        # Membro normal não pode deletar contribuições
        self.client.login(identifier="maria@carmelo.org", password="SenhaForte123!")
        url = reverse(
            "delete_contribution",
            kwargs={"user": self.member.slug, "id": contrib.id},
        )
        response = self.client.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Contribution.objects.filter(pk=contrib.pk).exists())

    # ==========================================================
    # VIEW: edit/update contribution
    # ==========================================================

    def test_edit_contribution_loads_form(self):
        contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse(
            "edit_contribution",
            kwargs={"user": self.member.slug, "id": contrib.id},
        )
        response = self.client.get(url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editar Contribuição")
        self.assertContains(response, f'value="2024-07-10"')

    def test_update_contribution_changes_price_and_date(self):
        contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse(
            "update_contribution",
            kwargs={"user": self.member.slug, "id": contrib.id},
        )
        response = self.client.post(
            url,
            {"date_pay": "2024-07-15", "price": "75.00"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        contrib.refresh_from_db()
        self.assertEqual(contrib.date_pay.isoformat(), "2024-07-15")
        self.assertEqual(float(contrib.price), 75.00)

    def test_update_contribution_blank_price_keeps_current(self):
        contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse(
            "update_contribution",
            kwargs={"user": self.member.slug, "id": contrib.id},
        )
        response = self.client.post(
            url, {"date_pay": "2024-07-10", "price": ""}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        contrib.refresh_from_db()
        self.assertEqual(float(contrib.price), 50.00)

    def test_update_contribution_rejects_duplicate_month(self):
        Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        contrib2 = Contribution.objects.create(
            price="60.00",
            date_pay="2024-08-05",
            carmel=self.carmel,
            member=self.member,
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        # Tenta mover contrib2 para julho (mês já ocupado)
        url = reverse(
            "update_contribution",
            kwargs={"user": self.member.slug, "id": contrib2.id},
        )
        response = self.client.post(
            url, {"date_pay": "2024-07-20", "price": "60.00"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        contrib2.refresh_from_db()
        self.assertEqual(contrib2.date_pay.isoformat(), "2024-08-05")
        self.assertContains(response, "já possui uma contribuição")

    def test_update_contribution_requires_permission(self):
        contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        self.client.login(identifier="maria@carmelo.org", password="SenhaForte123!")
        url = reverse(
            "update_contribution",
            kwargs={"user": self.member.slug, "id": contrib.id},
        )
        response = self.client.post(
            url, {"date_pay": "2024-07-15", "price": "75.00"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 403)

    def test_csrf_token_always_present_for_hx_post(self):
        """O token CSRF deve existir na página mesmo sem forms pendentes.

        O botão de deletar usa hx-post; sem um input csrfmiddlewaretoken na
        página o handler global do HTMX não envia o token e o Django responde
        403 (regressão conhecida).
        """
        # Membro cuja entrada é o mês atual e que já pagou o mês atual:
        # count_missing == 0, então NENHUM form pendente é renderizado e o
        # token só pode vir do {% csrf_token %} global do base.html.
        today = date.today()
        first_day_of_month = today.replace(day=1)
        self.member.entry_date = first_day_of_month
        self.member.save()
        Contribution.objects.create(
            price="50.00",
            date_pay=today,
            carmel=self.carmel,
            member=self.member,
        )

        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        response = self.client.get(
            reverse("contribution_member", kwargs={"slug": self.member.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_delete_contribution_works_with_real_csrf(self):
        """Fluxo real do navegador: POST com token CSRF extraído da página.

        Simula o handler htmx:configRequest do base.html, que injeta o token
        do input csrfmiddlewaretoken no header X-CSRFToken.
        """
        from django.test import Client

        contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        client = Client(enforce_csrf_checks=True)
        client.login(identifier="manager@carmelo.org", password="SenhaForte123!")

        page = client.get(
            reverse("contribution_member", kwargs={"slug": self.member.slug})
        )
        html = page.content.decode()
        import re

        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
        self.assertIsNotNone(match, "Token CSRF não encontrado na página")
        token = match.group(1)

        url = reverse(
            "delete_contribution",
            kwargs={"user": self.member.slug, "id": contrib.id},
        )
        response = client.post(
            url,
            {},
            HTTP_HX_REQUEST="true",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contribution.objects.filter(pk=contrib.pk).exists())

    # ==========================================================
    # FINANCIAL REPORT
    # ==========================================================

    def test_financial_report_requires_login(self):
        response = self.client.get(reverse("financial_report"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_financial_report_requires_money_permission(self):
        self.client.login(identifier="maria@carmelo.org", password="SenhaForte123!")
        response = self.client.get(reverse("financial_report"))
        self.assertEqual(response.status_code, 403)

    def test_manager_sees_own_carmel_report(self):
        Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        response = self.client.get(reverse("financial_report"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Relatório Financeiro")
        self.assertContains(response, self.carmel.name)
        self.assertNotContains(response, "Por Carmelo")  # não é global

    def test_staff_sees_global_report(self):
        from django.contrib.auth import get_user_model

        staff = get_user_model().objects.create_user(
            email="admin@carmelo.org",
            name="Admin Sistema",
            password="SenhaForte123!",
            church="Paróquia Central",
            entry_date="2020-01-01",
            carmel=self.carmel,
            roles="NM",
        )
        staff.is_staff = True
        staff.save()

        self.client.login(identifier="admin@carmelo.org", password="SenhaForte123!")
        response = self.client.get(reverse("financial_report"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Relatório Financeiro Global")
        self.assertContains(response, "Por Carmelo")
