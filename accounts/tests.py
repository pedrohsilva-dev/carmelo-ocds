from django.test import TestCase
from django.urls import reverse

from carmel.models import Carmel
from members.models import Member


class LoginFlowTests(TestCase):

    def setUp(self):
        self.carmel = Carmel.objects.create(
            name="Carmelo Teste",
            description="Comunidade de teste",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
            diocese="Diocese de Itapetininga",
            city="Itapetininga",
        )
        self.password = "SenhaForte123!"
        self.member = Member.objects.create_user(
            email="joao@carmelo.org",
            name="João da Silva",
            password=self.password,
            church="Paróquia São José",
            entry_date="2024-01-01",
            carmel=self.carmel,
            roles="NM",
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email ou Nome")

    def test_login_by_email(self):
        response = self.client.post(
            reverse("login"),
            {"identifier": "joao@carmelo.org", "password": self.password},
        )
        self.assertRedirects(response, reverse("profile"))

    def test_login_by_name(self):
        response = self.client.post(
            reverse("login"),
            {"identifier": "João da Silva", "password": self.password},
        )
        self.assertRedirects(response, reverse("profile"))

    def test_login_wrong_password(self):
        response = self.client.post(
            reverse("login"),
            {"identifier": "joao@carmelo.org", "password": "senha-errada"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "incorretos")

    def test_login_case_insensitive_name(self):
        response = self.client.post(
            reverse("login"),
            {"identifier": "joão da silva", "password": self.password},
        )
        self.assertRedirects(response, reverse("profile"))

    def test_authenticated_user_is_redirected_to_profile(self):
        self.client.login(identifier="joao@carmelo.org", password=self.password)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("profile"))

    def test_next_redirect_is_honored(self):
        next_url = reverse("profile")
        response = self.client.post(
            reverse("login"),
            {"identifier": "joao@carmelo.org", "password": self.password, "next": next_url},
        )
        self.assertRedirects(response, next_url)

    def test_logout(self):
        self.client.login(identifier="joao@carmelo.org", password=self.password)
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))


class LayoutSidebarTests(TestCase):
    """A margem esquerda da sidebar (260px) só deve valer para usuários logados.

    O CSS aplica `main { margin-left: 260px }` apenas quando o <body> tem a
    classe `is-authenticated`. Páginas públicas (login/home) não têm sidebar
    e devem ficar centralizadas.
    """

    def setUp(self):
        self.carmel = Carmel.objects.create(
            name="Carmelo Teste",
            description="Comunidade de teste",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
        )
        self.password = "SenhaForte123!"
        self.member = Member.objects.create_user(
            email="joao@carmelo.org",
            name="João da Silva",
            password=self.password,
            church="Paróquia São José",
            entry_date="2024-01-01",
            carmel=self.carmel,
            roles="NM",
        )

    def _body_tag(self, html):
        import re

        match = re.search(r"<body[^>]*>", html)
        return match.group(0) if match else ""

    def test_anonymous_login_page_has_no_auth_class(self):
        """Login deslogado: body SEM is-authenticated → sem margem da sidebar."""
        response = self.client.get(reverse("login"))
        self.assertNotIn("is-authenticated", self._body_tag(response.content.decode()))

    def test_anonymous_home_has_no_auth_class(self):
        """Landing deslogada: body SEM is-authenticated → conteúdo centralizado."""
        response = self.client.get(reverse("home"))
        self.assertNotIn("is-authenticated", self._body_tag(response.content.decode()))

    def test_authenticated_page_has_auth_class(self):
        """Página logada: body COM is-authenticated → margem da sidebar aplicada."""
        self.client.login(identifier="joao@carmelo.org", password=self.password)
        response = self.client.get(reverse("profile"))
        self.assertIn("is-authenticated", self._body_tag(response.content.decode()))


class SidebarMarginCssTests(TestCase):
    """A margem de 260px da sidebar deve estar escopada ao usuário logado.

    Regressão: a regra `main { margin-left: 260px }` sem escopo deslocava o
    login/home deslogados 260px para a direita. O CSS precisa aplicar a margem
    apenas em `body.is-authenticated` — tanto na fonte (static/) quanto na
    cópia de produção (staticfiles/, servida pelo WhiteNoise).
    """

    def _read_css(self, rel_path):
        from django.contrib.staticfiles import finders

        found = finders.find(rel_path)
        self.assertIsNotNone(found, f"CSS não encontrado: {rel_path}")
        with open(found, encoding="utf-8") as f:
            return f.read()

    def _assert_scoped(self, css):
        import re

        self.assertIn("body.is-authenticated main", css)
        self.assertIn("margin-left: 260px", css)
        # A regra antiga (desescopada) não deve existir: nenhum bloco
        # `main { ... }` sem o escopo .is-authenticated pode ter a margem.
        for match in re.finditer(r"([^{}]*?)\s*main\s*\{([^}]*?)}", css):
            prefix, body = match.group(1), match.group(2)
            if "margin-left: 260px" in body and "is-authenticated" not in prefix:
                self.fail(f"Regra antiga desescopada encontrada: {match.group(0)}")

    def test_source_css_has_scoped_margin(self):
        self._assert_scoped(self._read_css("css/modules/12-utilities.css"))

    def test_staticfiles_css_has_scoped_margin(self):
        # staticfiles/ é o que o WhiteNoise serve em produção (DEBUG=False)
        from django.conf import settings
        import os

        prod_path = os.path.join(settings.STATIC_ROOT, "css/modules/12-utilities.css")
        self.assertTrue(os.path.exists(prod_path), f"Faltou {prod_path}")
        with open(prod_path, encoding="utf-8") as f:
            self._assert_scoped(f.read())

    def test_not_authenticated_main_explicitly_centered(self):
        """Garantia explícita de que o main deslogado fica centralizado."""
        css = self._read_css("css/modules/12-utilities.css")
        self.assertIn("body:not(.is-authenticated) main", css)
        self.assertIn("margin-left: 0", css)


class ProfileCrudTests(TestCase):
    """CRUD de telefones e endereço do próprio perfil."""

    def setUp(self):
        self.carmel = Carmel.objects.create(
            name="Carmelo Teste",
            description="Comunidade de teste",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
        )
        self.password = "SenhaForte123!"
        self.member = Member.objects.create_user(
            email="joao@carmelo.org",
            name="João da Silva",
            password=self.password,
            church="Paróquia São José",
            entry_date="2024-01-01",
            carmel=self.carmel,
            roles="NM",
        )
        self.client.login(identifier="joao@carmelo.org", password=self.password)

    # ==========================================================
    # PHONES
    # ==========================================================

    def test_register_phone(self):
        response = self.client.post(
            reverse("register_phone"),
            {"name": "Casa", "phone": "(15) 99999-1111"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        from members.models import Phone

        self.assertTrue(
            Phone.objects.filter(
                member=self.member, number="(15) 99999-1111"
            ).exists()
        )

    def test_duplicate_phone_rejected(self):
        from members.models import Phone

        Phone.objects.create(member=self.member, name="Casa", number="(15) 99999-2222")
        response = self.client.post(
            reverse("register_phone"),
            {"name": "Casa", "phone": "(15) 99999-2222"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Phone.objects.filter(member=self.member, number="(15) 99999-2222").count(),
            1,
        )

    def test_delete_phone(self):
        from members.models import Phone

        phone = Phone.objects.create(
            member=self.member, name="Casa", number="(15) 99999-3333"
        )
        response = self.client.post(
            reverse("delete_phone", kwargs={"id": phone.id}), HTTP_HX_REQUEST="true"
        )
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
        response = self.client.post(
            reverse("register_address"), self._address_payload(), HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        from members.models import Address

        self.assertTrue(Address.objects.filter(member=self.member).exists())

    def test_edit_address(self):
        from members.models import Address

        Address.objects.create(member=self.member, street="Rua Velha", number="1")
        response = self.client.post(
            reverse("edit_address"),
            self._address_payload(street="Rua Nova"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertEqual(self.member.address.street, "Rua Nova")

    def test_delete_address(self):
        from members.models import Address

        Address.objects.create(member=self.member, street="Rua Velha", number="1")
        response = self.client.get(reverse("delete_address"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Address.objects.filter(member=self.member).exists())


class HomePageTests(TestCase):
    """Landing page exibe dados reais do Carmelo (OCDS Itapetininga)."""

    def setUp(self):
        self.carmel = Carmel.objects.create(
            name="OCDS Itapetininga",
            description="Comunidade de teste",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
            diocese="Diocese de Itapetininga",
            city="Itapetininga",
        )

    def test_home_renders_carmel_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OCDS Itapetininga")

    def test_home_renders_carmel_city_and_diocese(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Itapetininga")
        self.assertContains(response, "Diocese de Itapetininga")

    def test_home_renders_carmel_description(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Comunidade de teste")

    def test_home_works_without_carmel(self):
        """Sem registro de carmelo, a landing usa fallbacks legíveis."""
        Carmel.objects.all().delete()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OCDS Itapetininga")

    def test_home_navbar_has_anchor_links(self):
        """Navbar da landing tem âncoras para as seções da mesma página."""
        response = self.client.get(reverse("home"))
        html = response.content.decode()
        for anchor in ["#hp-inicio", "#hp-carmelo", "#hp-historia",
                       "#hp-espiritualidade", "#hp-formacao", "#hp-contato"]:
            self.assertIn(f'href="{anchor}"', html, f"Faltou âncora {anchor}")

    def test_home_navbar_has_login_button(self):
        """Botão de login visível no navbar da landing para visitantes."""
        response = self.client.get(reverse("home"))
        html = response.content.decode()
        self.assertIn(reverse("login"), html)
        self.assertIn("Entrar", html)


class ProtectedRoutesTests(TestCase):
    """Todas as rotas do sistema exigem login, exceto home e login."""

    def setUp(self):
        self.carmel = Carmel.objects.create(
            name="Carmelo Teste",
            description="Comunidade de teste",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
        )
        self.member = Member.objects.create_user(
            email="ana@carmelo.org",
            name="Ana Souza",
            password="SenhaForte123!",
            church="Paróquia São José",
            entry_date="2024-01-01",
            carmel=self.carmel,
            roles="NM",
        )
        self.manager = Member.objects.create_user(
            email="gestor@carmelo.org",
            name="Gestor Carmelo",
            password="SenhaForte123!",
            church="Paróquia São José",
            entry_date="2023-01-01",
            carmel=self.carmel,
            roles="MN",
        )
        self.other_carmel = Carmel.objects.create(
            name="Outro Carmelo",
            description="Comunidade irmã",
            price_contribution_default="40.00",
            pay_day_contribution_default=5,
        )
        self.other_member = Member.objects.create_user(
            email="bia@outro.org",
            name="Bia Lima",
            password="SenhaForte123!",
            church="Paróquia Santa Rita",
            entry_date="2024-03-01",
            carmel=self.other_carmel,
            roles="NM",
        )

    def test_home_is_public(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_login_is_public(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def _assert_protected(self, url_name, kwargs=None):
        url = reverse(url_name, kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302, f"{url_name} deveria redirecionar")
        self.assertIn(reverse("login"), response.url)

    def test_protected_routes_without_params(self):
        for name in [
            "profile",
            "list_member",
            "register_member",
            "carmel_profile",
            "edit_carmel",
            "votes_registration",
            "financial_report",
        ]:
            self._assert_protected(name)

    def test_protected_routes_with_params(self):
        self._assert_protected("show_member", {"slug": self.member.slug})
        self._assert_protected("update_member", {"id": self.member.id})
        self._assert_protected("delete_member", {"id": self.member.id})
        self._assert_protected("transfer_member", {"id": self.member.id})
        self._assert_protected("contribution_member", {"slug": self.member.slug})
        self._assert_protected("votes_members", {"slug": self.member.slug})
        self._assert_protected("register_contribution", {"user": self.member.slug})
        self._assert_protected("delete_contribution", {"id": 1, "user": self.member.slug})
        self._assert_protected("register_vote")
        self._assert_protected("register_votes_registration")

    def test_other_carmel_member_is_404_not_visible(self):
        # Manager de um carmelo não deve enxergar membro de outro carmelo
        self.client.login(identifier="gestor@carmelo.org", password="SenhaForte123!")
        response = self.client.get(
            reverse("show_member", kwargs={"slug": self.other_member.slug})
        )
        self.assertEqual(response.status_code, 404)

    def test_all_routes_require_login_except_home_and_login(self):
        """Enumerates every URL pattern and asserts anonymous users are
        redirected to login — guaranteeing no route is accidentally open.

        O admin do Django e as rotas com parâmetros dinâmicos (exigem objetos)
        são excluídos: o admin tem seu próprio mecanismo de login e as rotas
        parametrizadas são cobertas nos testes específicos.
        """
        from django.urls import get_resolver

        public_names = {"home", "login"}
        checked = []

        def walk(patterns, namespace=""):
            for pattern in patterns:
                name = getattr(pattern, "name", None)

                # Rotas com parâmetros dinâmicos exigem objetos reais
                converters = getattr(
                    getattr(pattern, "pattern", None), "converters", {}
                )
                if converters:
                    continue

                if hasattr(pattern, "url_patterns"):
                    ns = pattern.namespace or namespace
                    if ns == "admin":
                        continue
                    walk(pattern.url_patterns, ns)
                    continue

                if not name or name in public_names:
                    continue

                full_name = f"{namespace}:{name}" if namespace else name

                try:
                    url = reverse(full_name)
                except Exception:
                    continue

                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    302,
                    f"Rota '{full_name}' ({url}) deveria redirecionar anônimos ao login",
                )
                self.assertIn(reverse("login"), response.url, full_name)
                checked.append(full_name)

        walk(get_resolver().url_patterns)

        self.assertGreater(
            len(checked), 10, f"Enumeração cobriu apenas {len(checked)} rotas"
        )
