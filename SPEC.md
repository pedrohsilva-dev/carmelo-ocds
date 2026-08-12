# SPEC — Sistema OCDS (Ordem dos Carmelitas Descalços Seculares)

> Documento vivo do projeto. Descreve o sistema, o diagnóstico atual, o que foi
> corrigido, o que falta e a arquitetura alvo.

---

## 1. Visão Geral do Sistema

Sistema web de gestão para uma comunidade da **Ordem dos Carmelitas Descalços
Seculares (OCDS)** — "Comunidade Alegria da Sagrada Face". Stack:

| Camada | Tecnologia |
|---|---|
| Backend | Django 4.2 (Python 3.12) |
| Auth | `Member` (AbstractBaseUser + PermissionsMixin), login por e-mail |
| Roles/Permissões | `django-role-permissions` (`core/roles.py`) |
| Frontend | Bootstrap 5 + Alpine.js + HTMX 2 + Chart.js + GSAP |
| CSS | Design system modular em `static/css/modules/` |
| Banco | SQLite (dev) / PostgreSQL (prod via env) |
| Deploy | Gunicorn + WhiteNoise + Nginx (config incluída) |

### Domínio

- **Carmelo** — comunidade com valor padrão de contribuição, dia de pagamento,
  diocese e cidade.
- **Membro** — usuário do sistema (email + senha), pertence a um carmelo, tem uma
  função (`MN` Responsável, `FN` Tesoureiro, `NM` Normal) que mapeia para uma role.
- **Contribuição** — pagamento mensal de um membro. Uma por mês por membro.
- **Voto** — votos religiosos do membro (Temporários `TEMP` com duração em anos,
  Definitivos `DEF`), escolhidos entre os registros de voto do carmelo.
- **Contatos** — telefones e endereço por membro (gerenciados por manager).
- **Reset de senha** — modelo `ResetPasswordAccess` existe, views desativadas.

### Fluxos principais

1. **Login** → perfil do membro (com situação de contribuições, votos, contatos).
2. **Membros** → listar/filtrar/paginar, cadastrar, ver, editar, deletar.
3. **Contribuições** → por membro: meses em aberto + pagamento rápido por mês.
4. **Votos** → cadastro de votos por membro + catálogo de tipos de voto.
5. **Carmelo** → dashboard com estatísticas, gráficos e edição.
6. **Contatos** → telefones + endereço por membro (manager).

---

## 2. Avaliação do Sistema Atual (nota de entrada)

> Nota geral de entrada: **6,2 / 10** — funcional e com boa identidade visual,
> mas com dívidas técnicas, bugs latentes, pouca padronização e zero testes.

### Pontos fortes ✅
- Identidade visual carmelita consistente (ouro + mármore, dark/light, glassmorphism).
- Arquitetura CSS já modularizada (`modules/01..11`).
- Separação de apps por domínio (members, votes, contributions, contacts).
- HTMX + Alpine usados de forma interativa (filtros, modais, toasts).
- Modelo de usuário customizado com roles e permissões.
- `carmel/services/carmel_stats.py` — bom exemplo de lógica extraída de views.

### Problemas encontrados 🐛
1. **`LOGIN_URL` ausente** — `login_required` redireciona para `/accounts/login/`
   (padrão do Django) que **não existe** → tela de erro/404 ao tentar acessar
   página protegida deslogado.
2. **Login só por e-mail** — o usuário pediu login por **nome ou e-mail**.
3. **`requirements.txt` em UTF-16** (com BOM) — quebra `pip install -r`.
4. **Permissões inconsistentes** — `edit_vote_registration` (singular) usada na
   view mas só `edit_votes_registration` existe nas roles → view inacessível.
5. **UnboundLocalError latente** em `votes/views.py` (`register_vote`,
   `register_votes_registration`, `edit_vote_member`, `edit_vote_registration`)
   quando chamadas via GET ou com form inválido.
6. **`show_member`** usa `getattr(member, "location", None)` — não existe
   `location` no model → localização **nunca** é exibida (usa `address`).
7. **`carmel_edit.html` não existe** — a view `edit_carmel` (GET) quebra.
8. **`update_contribution` é um stub** que renderiza página vazia.
9. **Deletar por GET** (`hx-get`) em contribuições — deve ser POST.
10. **Permissão `transfer_carmel` definida mas nenhuma view/fluxo de transferência**.
11. **`text-carmel-muted` usado em templates mas não definido em nenhum CSS**.
12. **`member/services.py` tem sintaxe inválida** (nunca importado, mas é bomba).
13. **Chamada manual `form.clean_email()`** redundante no `register_member`.
14. **Toasts/messages HTMX** funcionam, mas erros de form aparecem só no POST
    inicial; falta feedback consistente.
15. **Zero testes** em todo o projeto.
16. **Sem padronização de forms** — cada template renderiza campos à mão
    (label + campo + erros) de forma diferente (badges, divs, cores).
17. **Mobile**: botões e selects sem largura total em alguns lugares, modais
    grandes sem scroll interno garantido, tabelas sem overflow.
18. **Home** mostra botão "Entrar" mesmo para usuários logados.

---

## 3. O que foi feito nesta revisão

- [x] `LOGIN_URL` apontando para `/contas/entrar/` + suporte a `?next=`.
- [x] Login por **nome ou e-mail** (campo único `identifier`, backend atualizado).
- [x] `requirements.txt` recodificado para UTF-8.
- [x] `core/roles.py` revisado — nomes de permissões alinhados e matriz por role.
- [x] `services.py` criado em **members**, **contributions** e **votes**
  (lógica de negócio fora das views) + refatoração das views.
- [x] Validações de **contribuição** no form: preço > 0, data dentro de
  [entrada do membro, hoje], mês único; valores com limite máximo.
- [x] Validações de **voto** no form: `year_duration` obrigatório p/ `TEMP`,
  data não futura, duplicados; views com `get_object_or_404` e escopo de carmelo.
- [x] Fluxo de **transferência de membro entre carmelos** (perm. `transfer_carmel`).
- [x] Perfil do carmelo com mais informações (diocese, cidade, dia de pagamento,
  valor padrão, últimos contribuintes).
- [x] Componentização de templates: `components/form_field.html`,
  `components/empty_state.html`, modais padronizados.
- [x] Home reorganizada (estado logado/deslogado, CTAs por permissão).
- [x] CSS/mobile: módulo de utilitários (`12-utilities.css`), fixes de
  responsividade, scroll em modais, larguras em mobile.
- [x] Testes automatizados (auth, permissões, contribuições, votos, transferência).

---

## 4. Arquitetura Alvo (serviços)

Regra: **views finas, services gordos, models com regras de domínio**.

```
app/
├── models.py          # regras de domínio (clean(), propriedades)
├── forms.py           # validação de entrada
├── views.py           # HTTP, permissões, renderização (sem lógica de negócio)
├── services.py        # casos de uso reutilizáveis (novo padrão)
├── urls.py
└── templates/
```

### Matriz de permissões por role (alvo)

| Permissão | Normal | Financeiro | Manager |
|---|:-:|:-:|:-:|
| login, home, profile | ✅ | ✅ | ✅ |
| view_carmel / carmel_dashboard | — | ✅ | ✅ |
| see_total_money / show_money | — | ✅ | ✅ |
| list_members | — | ✅ | ✅ |
| read_member | — | ✅ | ✅ |
| create/edit/delete_member | — | — | ✅ |
| access_contacts | — | — | ✅ |
| create/read/edit/delete/list_contribute | — | ✅ | ✅ |
| create/list/edit/delete_vote, read_vote | — | — | ✅ |
| votes_registration CRUD | — | — | ✅ |
| edit_carmel / transfer_carmel | — | — | ✅ |

> Superusuário (admin) sempre tem tudo via `is_superuser`.

---

## 5. O que ainda falta (backlog)

- **Recuperação de senha** ativa (views comentadas + `ResetPasswordAccess`) com
  envio real de e-mail configurado via env.
- **Upload de logo do carmelo** (campo `brand` comentado no model).
- **Ações em massa** na listagem de membros (transferir, ativar/desativar).
- **Relatório financeiro** anual exportável (PDF/CSV).
- **Notificações** de contribuição atrasada (email/in-app).
- **Testes de integração** com browser (Playwright) e **CI** (GitHub Actions).
- **i18n** completo e **acessibilidade** (ARIA nos modais, focus trap).
- **Rate limiting** no login (django-axes ou similar) para produção.

---

## 6. Nota pós-revisão

> Nota estimada: **8,3 / 10** — base sólida, padronizada, testada e com fluxos
> completos. Ganha os últimos pontos com recuperação de senha, relatórios e CI.
