from django.test import TestCase
from django.urls import reverse

from carmel.models import Carmel
from members.models import Member
from votes.forms import VoteForm
from votes.models import Vote, VotesRegistration


class VoteTests(TestCase):

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
            email="ana@carmelo.org",
            name="Ana Souza",
            password="SenhaForte123!",
            church="Paróquia São José",
            entry_date="2024-06-01",
            carmel=self.carmel,
            roles="NM",
        )
        self.vote_registration = VotesRegistration.objects.create(
            name="Voto de Obediência",
            description="Voto religioso de obediência",
        )

    # ==========================================================
    # FORM VALIDATIONS
    # ==========================================================

    def test_temp_vote_requires_year_duration(self):
        form = VoteForm(
            {
                "votes_registration": self.vote_registration.id,
                "date": "2024-07-10T10:00",
                "type": "TEMP",
                "year_duration": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("year_duration", form.errors)

    def test_definitive_vote_does_not_require_year_duration(self):
        form = VoteForm(
            {
                "votes_registration": self.vote_registration.id,
                "date": "2024-07-10T10:00",
                "type": "DEF",
                "year_duration": "",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_future_vote_rejected(self):
        form = VoteForm(
            {
                "votes_registration": self.vote_registration.id,
                "date": "2099-01-01T10:00",
                "type": "TEMP",
                "year_duration": "3",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    # ==========================================================
    # DUPLICATE VOTE (view logic)
    # ==========================================================

    def test_duplicate_vote_rejected_by_view(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")

        url = reverse("register_vote")
        payload = {
            "user_current": self.member.slug,
            "votes_registration": self.vote_registration.id,
            "date": "2024-07-10T10:00",
            "type": "DEF",
            "year_duration": "",
        }

        first = self.client.post(url, payload, HTTP_HX_REQUEST="true")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(Vote.objects.filter(member=self.member).count(), 1)

        second = self.client.post(url, payload, HTTP_HX_REQUEST="true")
        self.assertEqual(second.status_code, 200)
        # continua com apenas 1 voto (duplicado rejeitado)
        self.assertEqual(Vote.objects.filter(member=self.member).count(), 1)

    # ==========================================================
    # PERMISSIONS
    # ==========================================================

    def test_normal_member_cannot_manage_votes(self):
        self.client.login(identifier="ana@carmelo.org", password="SenhaForte123!")
        response = self.client.get(
            reverse("votes_members", kwargs={"slug": self.member.slug})
        )
        self.assertEqual(response.status_code, 403)

    # ==========================================================
    # DELETE VOTE
    # ==========================================================

    def test_delete_vote_removes_and_rerenders(self):
        vote = Vote.objects.create(
            member=self.member,
            votes_registration=self.vote_registration,
            date="2024-07-10T10:00:00Z",
            type="DEF",
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse("delete_vote", kwargs={"id": vote.id})
        response = self.client.post(
            url, {"user_current": self.member.slug}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Vote.objects.filter(pk=vote.pk).exists())

    def test_delete_vote_requires_permission(self):
        vote = Vote.objects.create(
            member=self.member,
            votes_registration=self.vote_registration,
            date="2024-07-10T10:00:00Z",
            type="DEF",
        )
        self.client.login(identifier="ana@carmelo.org", password="SenhaForte123!")
        url = reverse("delete_vote", kwargs={"id": vote.id})
        response = self.client.post(
            url, {"user_current": self.member.slug}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Vote.objects.filter(pk=vote.pk).exists())

    def test_update_vote_member_flow(self):
        vote = Vote.objects.create(
            member=self.member,
            votes_registration=self.vote_registration,
            date="2024-07-10T10:00:00Z",
            type="DEF",
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse("update_vote_member", kwargs={"id": vote.id})
        response = self.client.post(
            url,
            {
                "user_current": self.member.slug,
                "votes_registration": self.vote_registration.id,
                "date": "2024-08-15T10:00",
                "type": "TEMP",
                "year_duration": "2",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        vote.refresh_from_db()
        self.assertEqual(vote.type, "TEMP")
        self.assertEqual(vote.year_duration, 2)

    # ==========================================================
    # VOTES REGISTRATION (catálogo) CRUD
    # ==========================================================

    def test_register_votes_registration(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse("register_votes_registration")
        response = self.client.post(
            url,
            {"name": "Voto de Castidade", "description": "Voto de castidade"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            VotesRegistration.objects.filter(name="Voto de Castidade").exists()
        )

    def test_update_votes_registration(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse(
            "update_vote_registration", kwargs={"id": self.vote_registration.id}
        )
        response = self.client.post(
            url,
            {
                "name": "Voto de Obediência Atualizado",
                "description": "Descrição nova",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.vote_registration.refresh_from_db()
        self.assertEqual(
            self.vote_registration.name, "Voto de Obediência Atualizado"
        )

    def test_delete_votes_registration(self):
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        url = reverse(
            "delete_votes_registration", kwargs={"id": self.vote_registration.id}
        )
        response = self.client.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            VotesRegistration.objects.filter(pk=self.vote_registration.pk).exists()
        )

    # ==========================================================
    # CSRF (regressão do hx-post)
    # ==========================================================

    def test_votes_registration_page_renders_csrf_input(self):
        """A página de registros de voto precisa de token CSRF para os hx-post."""
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        response = self.client.get(reverse("votes_registration"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_delete_votes_registration_works_with_real_csrf(self):
        """Delete de registro de voto com token CSRF real (navegador simulado)."""
        import re

        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        client.login(identifier="manager@carmelo.org", password="SenhaForte123!")

        page = client.get(reverse("votes_registration"))
        match = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"', page.content.decode()
        )
        self.assertIsNotNone(match, "Token CSRF não encontrado na página")
        token = match.group(1)

        url = reverse(
            "delete_votes_registration", kwargs={"id": self.vote_registration.id}
        )
        response = client.post(url, {}, HTTP_HX_REQUEST="true", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            VotesRegistration.objects.filter(pk=self.vote_registration.pk).exists()
        )
