"""
Teste de interface (integração ponta a ponta).

Percorre a aplicação inteira da mesma forma que um navegador:

- cada página é carregada com GET;
- o token CSRF é extraído do HTML renderizado (o mesmo input
  ``csrfmiddlewaretoken`` que o ``{% csrf_token %}`` gera);
- toda requisição que altera estado (POST/PUT/DELETE) envia o token no
  header ``X-CSRFToken`` — exatamente o que o handler ``htmx:configRequest``
  do ``base.html`` faz para as requisições HTMX;
- o cliente usa ``enforce_csrf_checks=True``, ou seja, a proteção CSRF do
  Django está REALMENTE ativa (como em produção).

Isso cobre o bug relatado: o botão "deletar" de contribuições respondia 403
por CSRF. O fluxo completo é validado aqui com token real.
"""

import re

from django.test import Client, TestCase
from django.urls import reverse

from carmel.models import Carmel
from contributions.models import Contribution
from members.models import Address, Member, Phone
from votes.models import Vote, VotesRegistration

PASSWORD = "SenhaForte123!"
CSRF_INPUT_RE = r'name="csrfmiddlewaretoken" value="([^"]+)"'


def extract_csrf(html: str):
    """Extrai o primeiro token CSRF do HTML renderizado (como o navegador faria)."""
    match = re.search(CSRF_INPUT_RE, html)
    return match.group(1) if match else None


class InterfaceFlowTests(TestCase):
    """Fluxos completos de interface com CSRF real."""

    @classmethod
    def setUpTestData(cls):
        cls.carmel = Carmel.objects.create(
            name="Carmelo Interface",
            description="Comunidade de teste da interface",
            price_contribution_default="50.00",
            pay_day_contribution_default=10,
            diocese="Diocese de Itapetininga",
            city="Itapetininga",
        )
        cls.other_carmel = Carmel.objects.create(
            name="Carmelo São José",
            description="Segundo carmelo para transferência",
            price_contribution_default="40.00",
            pay_day_contribution_default=5,
        )
        cls.manager = Member.objects.create_user(
            email="gestor@carmelo.org",
            name="Gestor Interface",
            password=PASSWORD,
            church="Paróquia São José",
            entry_date="2023-01-01",
            carmel=cls.carmel,
            roles="MN",
        )
        cls.member = Member.objects.create_user(
            email="membro@carmelo.org",
            name="Membro Interface",
            password=PASSWORD,
            church="Paróquia São José",
            entry_date="2024-06-01",
            carmel=cls.carmel,
            roles="NM",
        )

    def setUp(self):
        # Cliente com CSRF REALMENTE ativo (como um navegador de verdade)
        self.client = Client(enforce_csrf_checks=True)
        self.token = None

    # ==========================================================
    # HELPERS (simulam o navegador)
    # ==========================================================

    def get_page(self, url, **extra):
        """GET em uma URL esperando 200."""
        response = self.client.get(url, **extra)
        self.assertEqual(response.status_code, 200, f"GET {url} → {response.status_code}")
        return response

    def grab_csrf(self, url):
        """Carrega uma página e guarda o token CSRF renderizado nela."""
        response = self.get_page(url)
        token = extract_csrf(response.content.decode())
        self.assertIsNotNone(token, f"Página sem token CSRF: {url}")
        self.token = token
        return token

    def login_as(self, member):
        """Faz login pelo formulário real, com CSRF (como um usuário faria)."""
        self.grab_csrf(reverse("login"))
        response = self.client.post(
            reverse("login"),
            {"identifier": member.email, "password": PASSWORD},
            HTTP_X_CSRFTOKEN=self.token,
        )
        self.assertRedirects(response, reverse("profile"))
        # O login gira o token CSRF: pega o token NOVO da página pós-login
        self.grab_csrf(reverse("profile"))

    def post(self, url, data=None, **extra):
        """POST com o token CSRF no header X-CSRFToken (igual ao HTMX)."""
        return self.client.post(url, data or {}, HTTP_X_CSRFTOKEN=self.token, **extra)

    # ==========================================================
    # 1. PÁGINAS PÚBLICAS
    # ==========================================================

    def test_01_home_publica(self):
        """Landing page acessível sem login."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_02_login_sem_token_e_erro_de_credencial(self):
        """Login: página renderiza CSRF; credencial errada volta com erro (não 403)."""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

        # Na tela de login o botão "Entrar" da navbar não deve aparecer
        self.assertNotContains(response, 'class="btn btn-item px-4')

        token = extract_csrf(response.content.decode())
        response = self.client.post(
            reverse("login"),
            {"identifier": "naoexiste@carmelo.org", "password": "Errada123!"},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "incorretos")

    def test_14_sidebar_destaca_pagina_atual(self):
        """A sidebar marca com 'active' o item correspondente à página atual."""
        self.login_as(self.manager)

        def active_links(html):
            """Retorna os hrefs dos itens da sidebar que estão com a classe active."""
            return [
                href
                for cls, href in re.findall(
                    r'class="(sidebar-link[^"]*)"\s*href="([^"]+)"', html
                )
                if "active" in cls
            ]

        expected_by_page = {
            reverse("list_member"): ["/membros/"],
            reverse("carmel_profile"): ["/carmelo/"],
            reverse("profile"): ["/contas/perfil_do_membro/"],
            reverse("financial_report"): ["/membros/contribuicoes/relatorio-financeiro/"],
            reverse("votes_registration"): ["/membros/votos/votos_do_carmelo/"],
        }

        for url, expected in expected_by_page.items():
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"GET {url}")
            self.assertEqual(
                active_links(response.content.decode()),
                expected,
                f"Página {url}: item ativo incorreto na sidebar",
            )

        # Páginas internas de membro (detalhe/edição) continuam marcando "Membros".
        response = self.client.get(
            reverse("show_member", kwargs={"slug": self.member.slug})
        )
        self.assertEqual(
            active_links(response.content.decode()), ["/membros/"],
            "show_member deveria manter 'Membros' ativo",
        )

    # ==========================================================
    # 2. LOGIN / LOGOUT / PERFIL
    # ==========================================================

    def test_03_login_logout_e_protecao_de_rota(self):
        """Login com CSRF real → perfil; logout; rota protegida redireciona."""
        self.login_as(self.manager)
        self.get_page(reverse("profile"))

        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    # ==========================================================
    # 3. CSRF OBRIGATÓRIO (e a diferença entre CSRF e permissão)
    # ==========================================================

    def test_04_csrf_e_obrigatorio_e_permissao_403(self):
        """Sem token → 403 CSRF. Com token válido, mas sem permissão → 403 de permissão."""
        contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )
        url = reverse(
            "delete_contribution",
            kwargs={"user": self.member.slug, "id": contrib.id},
        )

        # SEM token CSRF → 403 (proteção CSRF ativa)
        response = self.client.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Contribution.objects.filter(pk=contrib.pk).exists())

        # COM token válido, mas membro NORMAL (sem permissão de deletar) → 403
        # por PERMISSÃO — não é problema de CSRF.
        self.login_as(self.member)
        response = self.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Contribution.objects.filter(pk=contrib.pk).exists())

    # ==========================================================
    # 4. MEMBROS
    # ==========================================================

    def test_05_membros_lista_filtro_detalhe_cadastro_edicao(self):
        """Lista, filtro HTMX, detalhe, cadastro e edição de membro."""
        self.login_as(self.manager)

        self.get_page(reverse("list_member"))
        self.get_page(
            reverse("list_filter_members")
            + "?filter_name=Membro&filter_active=active&filter_role=&filter_pending="
        )
        self.get_page(reverse("show_member", kwargs={"slug": self.member.slug}))

        # Cadastro
        self.grab_csrf(reverse("register_member"))
        response = self.post(
            reverse("register_member"),
            {
                "name": "Novo Membro Interface",
                "email": "novo@carmelo.org",
                "church": "Paróquia Central",
                "entry_date": "2024-06-15",
                "roles": "NM",
                "password": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertRedirects(response, reverse("list_member"))
        novo = Member.objects.get(email="novo@carmelo.org")

        # Edição
        self.grab_csrf(reverse("update_member", kwargs={"id": novo.id}))
        response = self.post(
            reverse("update_member", kwargs={"id": novo.id}),
            {
                "name": "Novo Membro Interface Editado",
                "email": "novo@carmelo.org",
                "church": "Paróquia Central",
                "entry_date": "2024-06-15",
                "roles": "NM",
            },
        )
        self.assertRedirects(response, reverse("list_member"))
        novo.refresh_from_db()
        self.assertEqual(novo.name, "Novo Membro Interface Editado")

    def test_06_membro_delete_htmx_com_csrf(self):
        """Deletar membro via hx-post com CSRF real → 200 e registro removido."""
        self.login_as(self.manager)
        vitima = Member.objects.create_user(
            email="deletar@carmelo.org",
            name="Membro Para Deletar",
            password=PASSWORD,
            church="Paróquia Central",
            entry_date="2024-06-01",
            carmel=self.carmel,
            roles="NM",
        )

        self.grab_csrf(reverse("list_member"))
        response = self.post(
            reverse("delete_member", kwargs={"id": vitima.id}),
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Member.objects.filter(pk=vitima.pk).exists())

    # ==========================================================
    # 5. CONTRIBUIÇÕES (o módulo do bug relatado)
    # ==========================================================

    def test_07_contribuicoes_registrar_editar_atualizar(self):
        """Lista, registrar (hx-post), carregar edição (hx-get) e atualizar (hx-post)."""
        self.login_as(self.manager)
        self.grab_csrf(
            reverse("contribution_member", kwargs={"slug": self.member.slug})
        )

        # Registrar
        response = self.post(
            reverse("register_contribution", kwargs={"user": self.member.slug}),
            {"date_pay": "2024-07-10", "price": "50.00"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        contrib = Contribution.objects.get(member=self.member, date_pay="2024-07-10")

        # Carregar formulário de edição
        response = self.client.get(
            reverse(
                "edit_contribution",
                kwargs={"user": self.member.slug, "id": contrib.id},
            ),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editar Contribuição")

        # Atualizar
        response = self.post(
            reverse(
                "update_contribution",
                kwargs={"user": self.member.slug, "id": contrib.id},
            ),
            {"date_pay": "2024-07-15", "price": "75.00"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        contrib.refresh_from_db()
        self.assertEqual(float(contrib.price), 75.00)

    def test_08_contribuicao_delete_fluxo_real(self):
        """O BUG RELATADO: deletar contribuição dava 403.

        Fluxo real do navegador: token extraído da página e enviado no header
        X-CSRFToken (como o handler htmx:configRequest do base.html). O delete
        deve responder 200 e remover a contribuição.
        """
        self.login_as(self.manager)
        contrib = Contribution.objects.create(
            price="50.00",
            date_pay="2024-07-10",
            carmel=self.carmel,
            member=self.member,
        )

        # Página da lista — token CSRF renderizado no HTML
        self.grab_csrf(
            reverse("contribution_member", kwargs={"slug": self.member.slug})
        )
        url = reverse(
            "delete_contribution",
            kwargs={"user": self.member.slug, "id": contrib.id},
        )
        response = self.post(url, {}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contribution.objects.filter(pk=contrib.pk).exists())
        self.assertContains(response, "Pagamentos Feitos")

    # ==========================================================
    # 6. VOTOS
    # ==========================================================

    def test_09_votos_flow_completo(self):
        """Registros de voto (catálogo) + votos do membro: criar e deletar."""
        self.login_as(self.manager)

        # Catálogo de votos — página + cadastro
        self.grab_csrf(reverse("votes_registration"))
        response = self.post(
            reverse("register_votes_registration"),
            {"name": "Voto de Teste", "description": "Descrição do voto de teste"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        vr = VotesRegistration.objects.get(name="Voto de Teste")

        # Votos do membro — página + registrar voto
        self.grab_csrf(reverse("votes_members", kwargs={"slug": self.member.slug}))
        response = self.post(
            reverse("register_vote"),
            {
                "user_current": self.member.slug,
                "date": "2024-07-10 10:00:00",
                "type": "TEMP",
                "votes_registration": vr.id,
                "year_duration": 2,
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        vote = Vote.objects.get(member=self.member, votes_registration=vr)

        # Deletar voto do membro (hx-post)
        response = self.post(
            reverse("delete_vote", kwargs={"id": vote.id}),
            {"user_current": self.member.slug},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Vote.objects.filter(pk=vote.pk).exists())

        # Deletar opção de voto do catálogo (hx-post)
        response = self.post(
            reverse("delete_votes_registration", kwargs={"id": vr.id}),
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(VotesRegistration.objects.filter(pk=vr.pk).exists())

    # ==========================================================
    # 7. CONTATOS (telefones e endereços)
    # ==========================================================

    def test_10_contatos_do_membro(self):
        """Contatos de um membro: telefone e endereço criar/deletar via hx-post."""
        self.login_as(self.manager)
        self.grab_csrf(
            reverse("contacts:index", kwargs={"member_slug": self.member.slug})
        )

        # Telefone
        response = self.post(
            reverse("contacts:register_phone", kwargs={"member_slug": self.member.slug}),
            {"name": "Celular", "number": "(15) 99999-1234"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        phone = Phone.objects.get(member=self.member, number="(15) 99999-1234")

        response = self.post(
            reverse("contacts:delete_phone", kwargs={"id": phone.id}),
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Phone.objects.filter(pk=phone.pk).exists())

        # Endereço
        addr_data = {
            "street": "Rua das Flores",
            "number": "123",
            "neighborhood": "Centro",
            "city": "Itapetininga",
            "state": "SP",
            "zipcode": "18200-000",
        }
        response = self.post(
            reverse("contacts:register_address", kwargs={"member_slug": self.member.slug}),
            addr_data,
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        address = Address.objects.get(member=self.member)

        response = self.post(
            reverse("contacts:delete_address", kwargs={"member_slug": self.member.slug}),
            {},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Address.objects.filter(pk=address.pk).exists())

    def test_11_contatos_do_proprio_perfil(self):
        """Telefone e endereço do PRÓPRIO usuário (módulo accounts)."""
        self.login_as(self.manager)
        self.grab_csrf(reverse("profile"))

        # Telefone
        response = self.post(
            reverse("register_phone"),
            {"name": "Casa", "phone": "(15) 3333-4444"},
        )
        self.assertEqual(response.status_code, 200)
        phone = Phone.objects.get(member=self.manager, number="(15) 3333-4444")

        response = self.post(reverse("delete_phone", kwargs={"id": phone.id}))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Phone.objects.filter(pk=phone.pk).exists())

        # Endereço: criar → editar → deletar
        addr_data = {
            "street": "Av. Paulista",
            "number": "1000",
            "neighborhood": "Bela Vista",
            "city": "São Paulo",
            "state": "SP",
            "zipcode": "01310-100",
        }
        response = self.post(reverse("register_address"), addr_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Address.objects.filter(member=self.manager).exists())

        addr_data["street"] = "Av. Paulista, 2000"
        response = self.post(reverse("edit_address"), addr_data)
        self.assertEqual(response.status_code, 200)

        response = self.post(reverse("delete_address"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Address.objects.filter(member=self.manager).exists())

    # ==========================================================
    # 8. CARMELO, FINANCEIRO E TRANSFERÊNCIA
    # ==========================================================

    def test_12_carmelo_financeiro_e_transferencia(self):
        """Perfil do carmelo, edição (POST), relatório financeiro e transferência."""
        self.login_as(self.manager)

        self.grab_csrf(reverse("carmel_profile"))
        response = self.post(
            reverse("edit_carmel"),
            {
                "name": self.carmel.name,
                "description": "Descrição atualizada",
                "city": "Itapetininga",
                "diocese": "Diocese de Itapetininga",
                "price_contribution_default": "55.00",
                "pay_day_contribution_default": 12,
            },
        )
        self.assertRedirects(response, reverse("carmel_profile"))
        self.carmel.refresh_from_db()
        self.assertEqual(float(self.carmel.price_contribution_default), 55.00)

        # Relatório financeiro
        response = self.client.get(reverse("financial_report"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Relatório Financeiro")

        # Transferência de membro para outro carmelo
        self.grab_csrf(reverse("transfer_member", kwargs={"id": self.member.id}))
        response = self.post(
            reverse("transfer_member", kwargs={"id": self.member.id}),
            {"target_carmel": self.other_carmel.id},
        )
        self.assertRedirects(response, reverse("list_member"))
        self.member.refresh_from_db()
        self.assertEqual(self.member.carmel_id, self.other_carmel.id)

    def test_13_staff_cria_carmelo(self):
        """Administrador (staff) cria um novo carmelo e vê relatório global."""
        staff = Member.objects.create_user(
            email="admin@carmelo.org",
            name="Admin Sistema",
            password=PASSWORD,
            church="Paróquia Central",
            entry_date="2020-01-01",
            carmel=self.carmel,
            roles="NM",
        )
        staff.is_staff = True
        staff.save()

        self.login_as(staff)
        self.grab_csrf(reverse("create_carmel"))
        response = self.post(
            reverse("create_carmel"),
            {
                "name": "Carmelo Novo",
                "description": "Novo carmelo criado via interface",
                "city": "Sorocaba",
                "diocese": "Diocese de Sorocaba",
                "price_contribution_default": "60.00",
                "pay_day_contribution_default": 15,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("carmel_profile"), response.url)
        self.assertTrue(Carmel.objects.filter(name="Carmelo Novo").exists())

        # Relatório financeiro global (staff)
        response = self.client.get(reverse("financial_report"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Relatório Financeiro Global")
