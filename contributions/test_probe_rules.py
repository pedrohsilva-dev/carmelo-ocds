from datetime import date

from django.test import TestCase
from django.urls import reverse

from carmel.models import Carmel
from contributions.models import Contribution
from members.models import Member


class ProbeUpdateRules2(TestCase):
    """Verifica o HTML renderizado no modal quando a atualizacao falha."""

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
            church="Paroquia Sao Jose",
            entry_date="2023-01-01",
            carmel=self.carmel,
            roles="MN",
        )
        self.member = Member.objects.create_user(
            email="maria@carmelo.org",
            name="Maria Oliveira",
            password="SenhaForte123!",
            church="Paroquia Sao Jose",
            entry_date="2024-06-01",
            carmel=self.carmel,
            roles="NM",
        )
        self.contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        self.client.login(identifier="manager@carmelo.org", password="SenhaForte123!")
        self.url = reverse(
            "update_contribution",
            kwargs={"user": self.member.slug, "id": self.contrib.id},
        )

    def _post(self, date_pay, price):
        return self.client.post(
            self.url,
            {"date_pay": date_pay, "price": price},
            HTTP_HX_REQUEST="true",
        )

    def test_probe_huge_price_html(self):
        r = self._post("2024-07-10", "999999999")
        html = r.content.decode()
        has_modal = "Editar Contribuicao" in html or "Editar Contribui" in html
        has_price_err = "m" in html  # placeholder
        # procura o texto de erro real com acento
        import re

        errs = re.findall(r"m[áa]ximo permitido", html)
        print(f"PROBE2 huge_price has_modal={has_modal} errors_found={errs}")
        # Tambem confirma se o modal ficou aberto com erro
        print(f"PROBE2 has_form_update_block={'form_update' in html}")

    def test_probe_modal_html_when_ok(self):
        r = self._post("2024-07-10", "60")
        html = r.content.decode()
        print(f"PROBE2 ok has_modal={'Editar Contribui' in html}")

    def test_probe_register_blank_price(self):
        """Cadastro com preco vazio usa o valor padrao do carmelo."""
        url = reverse(
            "register_contribution", kwargs={"user": self.member.slug}
        )
        r = self.client.post(
            url,
            {"date_pay": "2024-08-10", "price": ""},
            HTTP_HX_REQUEST="true",
        )
        contrib = Contribution.objects.filter(
            member=self.member, date_pay="2024-08-10"
        ).first()
        if contrib:
            print(f"PROBE2 register_blank saved_price={float(contrib.price)} default={float(self.carmel.price_contribution_default)}")
        else:
            print("PROBE2 register_blank NOT_SAVED")
