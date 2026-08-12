# Overview — O que foi feito

Documento-resumo de tudo o que foi implementado/corrigido nesta revisão do
sistema OCDS (Ordem dos Carmelitas Descalços Seculares).

> Complementa o `SPEC.md` (diagnóstico + backlog). O `ANTES.txt` traz a
> avaliação do sistema antigo.

---

## 1. Autenticação e sessão

- **Login por nome OU e-mail** — campo único `identifier`; backend
  `members/backends.py` autentica por `email` ou `name` (case-insensitive).
- `AUTHENTICATION_BACKENDS` registrado no `settings` (antes o backend existia,
  mas nunca era usado).
- `LOGIN_URL` apontando para `/contas/entrar/` (antes, `login_required`
  redirecionava para uma URL inexistente).
- Suporte a `?next=` no login (volta para a página de origem).
- Usuário já logado que acessa o login é redirecionado ao perfil.
- **Animação do login** aprimorada: entrada do card, brilho no botão, loading.

## 2. Permissões e roles

- `core/roles.py` revisado: nomes de permissões alinhados (ex.: o bug
  `edit_vote_registration` vs `edit_votes_registration`).
- `FinanceMember` agora também tem `read_member` (ver dados do membro).
- **Handlers de erro corrigidos**: 403/404/500 agora retornam o status HTTP
  correto (antes retornavam 200).

## 3. Services por app

Lógica de negócio extraída das views:

- `members/services.py` — filtros de membros, contagem de pendências,
  transferência entre carmelos, carmelos disponíveis.
- `contributions/services.py` — `month_empty` (meses pagos/faltantes).
- `votes/services.py` — votos do membro e catálogo de registros.
- `base/utils.py` — `paginate()` reutilizável.

## 4. Validações

- **Contribuições**: preço > 0, limite máximo, data não futura, data ≥ entrada
  do membro, mês único (model), fallback para o valor padrão do carmelo quando
  o preço é deixado em branco.
- **Votos**: `year_duration` obrigatório para votos temporários, data não
  futura, duplicidade (inclusive na edição).
- **Senhas**: validação de "senha == confirmação" e força da senha continuam
  **no form** (`MemberForm`/`MemberChangeForm`), como solicitado.

## 5. Fluxo de transferência de carmelo

- Nova view `transfer_member` (permissão `transfer_carmel`), página
  `members/transfer.html` com seletor de carmelo de destino, botão na tela do
  membro e redirecionamento correto após a transferência.

## 6. Models corrigidas

- `Carmel.price_contribution_default`: `max_digits=1000` → `max_digits=10`
  (+ validators) — migração `carmel/0002`.
- `Vote.year_duration`: validators 1–99 — migração `votes/0002`.
- `ResetPasswordAccess.save()`: não regenera o token em toda edição.
- Helpers no `Member`: `role_label`, `is_manager`, `is_finance`,
  `address_or_none`, `get_full_name`, etc.

## 7. Admin (Jazzmin) com identidade do sistema

- `JAZZMIN_SETTINGS` e `JAZZMIN_UI_TWEAKS` no `settings`: logo do sistema
  (`assets/brand_gold.png`), títulos, ícones por modelo, tema dark, UI builder.
- Admins completos: `MemberAdmin` com inlines (telefones, endereço,
  contribuições, votos), `VoteAdmin`, `ContributionAdmin`, `CarmelAdmin`.

## 8. Paginação em todas as listagens

- Componente `templates/partials/components/pagination.html` (HTMX ou links
  normais, com parâmetro de página configurável).
- Aplicado em: **contribuições** (10/pág), **votos** do membro (10/pág),
  **registros de voto** (12/pág), **telefones** (12/pág) e **votos do perfil**
  (10/pág). A listagem de membros já tinha.

## 9. Ações rápidas para responsáveis

- Seção "Ações Rápidas" na home para usuários logados com permissões
  (cadastrar membro, gerenciar membros, registrar contribuição, votos,
  painel do carmelo, editar carmelo) — exibida conforme a role.

## 10. CSS / Mobile

- Módulo `static/css/modules/12-utilities.css`: utilitários que faltavam
  (`text-carmel-muted`), estilos da sidebar, modais responsivos, cards de ação.
- Sidebar com saudação do usuário (avatar com inicial + nome + função).
- Navbar mobile com logo.
- Config global de CSRF para requisições HTMX fora de `<form>`.
- `collectstatic` atualizado.

## 11. Testes

- **32 testes** em 4 apps: `accounts` (login), `members` (roles, permissões,
  transferência), `contributions` (validações, mês único, valor padrão),
  `votes` (validações, duplicidade, permissões).
- Script **`test.sh`** para rodar separado ou junto, com ou sem cobertura:

```bash
./test.sh                    # todos
./test.sh members            # só um app
./test.sh members votes      # vários apps
./test.sh --coverage         # todos com relatório de cobertura
./test.sh members --coverage # um app com cobertura
```

## 12. Arquivos e organização

- `SPEC.md` — especificação do sistema, nota antes/depois, backlog.
- `ANTES.txt` — avaliação do sistema antigo.
- `overview.md` — este documento.
- `.gitignore` — `staticfiles/` (gerado em produção) e outros ajustes.
- `requirements.txt` — recodificado para UTF-8 (estava corrompido em UTF-16).
