# Project Carmel

Projeto Django para gestão de membros, contribuições, votações e perfis de carmel.

## Visão geral

- Baseado em Django 6.0.
- Autenticação personalizada com `members.Member` como modelo de usuário.
- Suporte a cadastro, login, perfil, telefone, endereço e recuperação de senha.
- Gestão de membros vinculados a um Carmelo (`carmel`), com visualização de perfil e contribuições.
- Aplicativos principais:
  - `accounts` — autenticação, perfil, telefones, endereços e reset de senha.
  - `members` — cadastro, visualização, edição e remoção de membros.
  - `carmel` — perfil do Carmelo e agregação de contribuições.
  - `contributions` — controle de contribuições de membros.
  - `votes` — registro e visualização de votos feitos pelos usuários.
  - `base` — templates de erros e middleware comum.

## Dependências

### Python

O projeto usa as seguintes dependências Python:

-asgiref==3.11.1
-certifi==2026.4.22
-charset-normalizer==3.4.7
-Django==6.0.3
-django-appconf==1.2.0
-django-extensions==4.1
-django-jazzmin==3.0.4
-django-libsass==0.9
-django-role-permissions==3.2.0
-django_compressor==4.6.0
-idna==3.14
-libsass==0.23.0
-MarkupSafe==3.0.3
-pydot==4.0.1
-pyparsing==3.3.2
-rcssmin==1.2.2
-requests==2.33.1
-rjsmin==1.2.5
-sqlparse==0.5.5
-tzdata==2025.3
-urllib3==2.7.0
-Werkzeug==3.1.8


### Node / frontend

O projeto também inclui dependências de frontend para SCSS/CSS:

- bootstrap
- sass
- postcss
- postcss-cli
- @fullhuman/postcss-purgecss

## Instalação

1. Crie e ative um ambiente virtual Python:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Instale as dependências Python:
   ```bash
   pip install -r requirements.txt
   ```

3. Instale dependências Node se precisar compilar estilos:
   ```bash
   npm install
   ```

4. Aplique migrações:
   ```bash
   python manage.py migrate
   ```

5. Crie um superusuário:
   ```bash
   python manage.py createsuperuser
   ```

6. Opcional: sincronize permissões de roles se houver comando disponível:
   ```bash
   python manage.py sync_roles
   ```

## Execução

Inicie o servidor Django:

```bash
python manage.py runserver
```

Acesse o projeto em `http://127.0.0.1:8000/`.

## Estrutura de URLs principais

- `/` — página inicial
- `/admin/` — painel administrativo Django
- `/accounts/login/` — login
- `/accounts/logout/` — logout
- `/accounts/profile/` — perfil do usuário
- `/accounts/forgot_password/` — recuperação de senha
- `/accounts/reset_password/<token>/` — redefinição de senha
- `/members/register/` — cadastro de membro
- `/members/` — seções de membros, votações e contribuições
- `/carmel/` — perfil do Carmelo

## Configuração adicional

- `core/settings.py` usa `DEBUG = True` e `ALLOWED_HOSTS = ['*']` em desenvolvimento.
- O banco de dados padrão é SQLite (`db.sqlite3`).
- `STATICFILES_DIRS` aponta para a pasta `static` e `STATIC_ROOT` está configurado para `staticfiles`.
- `django-compressor` está habilitado para compilação de SCSS.

## Notas

- O projeto está configurado para enviar e-mails de recuperação de senha no console durante o desenvolvimento.
- As rotas de perfil e dados de Carmelo exigem usuário autenticado.
- O aplicativo `jazzmin` fornece interface administrativa personalizada.

