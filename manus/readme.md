# Minha Carteira Digital (SGC)

Sistema de Gestão de Caixa para controle de finanças pessoais — receitas,
despesas, parcelas, recorrências, cartões e metas por categoria. Desenvolvido
em Django 5.2 com criptografia AES-256 de campos sensíveis.

---

## Funcionalidades

- **Dashboard** — balanço anual com crédito/débito/saldo por mês e gráficos por categoria
- **Transações** — CRUD completo com suporte a parcelas (grupos) e edição/exclusão em cascata
- **Registro rápido** — modal AJAX para lançamentos em poucos cliques
- **Calendário financeiro** — visualização mensal em grade com as transações do dia
- **Recorrências** — assinaturas/mensalidades que geram transações automaticamente (sem Celery)
- **Cartões** — CRUD + resumo de consumo com gráfico limite vs. usado
- **Metas** — limite de gasto por categoria/mês com indicador visual (verde/amarelo/vermelho)
- **Categorias** — globais ou por usuário (criadas automaticamente no cadastro)
- **Exportar CSV** — relatório mensal compatível com Excel (BOM UTF-8)
- **Segurança** — senhas, criptografia de campos sensíveis e reset de senha por email
- **Multi-usuário** — dados isolados por usuário (filtro por `user` em todas as queries)

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Django 5.2.10 |
| API | Django REST Framework 3.16 (instalado, sem uso ativo) |
| Banco | SQLite (`db.sqlite3`) |
| Criptografia | `cryptography` (AES-256 via `encrypted_model_fields`) |
| Config | `python-decouple` (`.env`) |
| Datas | `python-dateutil` |
| DB URL | `dj-database-url` |
| Frontend | Django Templates + Bootstrap + Bootstrap Icons + Chart.js |

---

## Pré-requisitos

- Python **3.13+**
- Pip

---

## Instalação

```bash
# 1. Clonar / entrar no diretório
cd minhacarteira

# 2. Criar e ativar virtualenv
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar arquivo .env (ver seção "Variáveis de ambiente" abaixo)

# 5. Migrar o banco
python manage.py migrate

# 6. Criar superusuário (opcional, para admin)
python manage.py createsuperuser

# 7. Rodar o servidor
python manage.py runserver
```

Acesse http://127.0.0.1:8000/

---

## Variáveis de ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto com:

```ini
SECRET_KEY=django-insecure-troque-esta-chave-por-uma-aleatoria
FIELD_ENCRYPTION_KEY=<chave-Fernet-de-44-bytes-base64>
DEBUG=True
ALLOWED_HOSTS=*
```

Gerar `FIELD_ENCRYPTION_KEY` (Fernet):

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Gerar `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> ⚠️ **Produção**: defina `DEBUG=False`, restrinja `ALLOWED_HOSTS`, use
> HTTPS e configure `EMAIL_BACKEND` para SMTP (atualmente é `console`).

---

## Estrutura do projeto

```
minhacarteira/
├── core/                  # Projeto Django (settings, urls globais)
│   ├── settings.py
│   └── urls.py
├── cal/                    # App principal (toda a lógica de negócio)
│   ├── models.py           # 7 modelos (Transacao, Recorrencia, Cartao, etc.)
│   ├── forms.py            # Forms de CRUD e cadastro de usuário
│   ├── services.py         # Cálculos financeiros centralizados
│   ├── utils.py            # Calendário HTML, parse mês/ano, backfill recorrências
│   ├── signals.py          # Cria categorias globais ao criar usuário
│   ├── context_processors.py # Saldos na navbar (chamado em todo request)
│   ├── admin.py
│   ├── urls.py
│   └── views/
│       ├── views_dashboard.py
│       ├── views_cal.py        # Calendário
│       ├── views_transacao.py  # CRUD de transações
│       ├── views_cartao.py     # CRUD de cartões + resumos
│       ├── views_recorrencia.py
│       ├── views_meta.py       # Metas por categoria
│       ├── views_categoria.py
│       ├── views_tipo.py
│       ├── views_user.py       # Perfil + admin de usuários
│       ├── views_login.py      # Cadastro
│       └── views_export.py     # Export CSV
├── encrypted_model_fields/  # Campos de modelo criptografados (lib local)
├── templates/                # Templates HTML (Django Templates)
│   ├── base.html
│   ├── navbar.html
│   ├── home.html
│   ├── cal/                  # Templates do app
│   ├── registration/         # login, register, logged_out
│   └── usuarios/             # perfil, listar, password_reset*
├── static/                  # CSS, JS, imagens
├── staticfiles/             # collectstatic output
├── logs/                    # logs do Django (auto-criada)
├── manage.py
├── db.sqlite3
├── requirements.txt
└── .env                     # variáveis (NÃO versionar)
```

---

## Comandos úteis

```bash
python manage.py runserver            # Servidor de desenvolvimento
python manage.py migrate              # Aplicar migrations
python manage.py makemigrations       # Criar migrations após mudar models
python manage.py createsuperuser     # Criar admin
python manage.py shell                # Shell interativo
python manage.py check                # Validar config do projeto
python manage.py collectstatic        # Coletar arquivos estáticos (produção)
```

---

## Regras de negócio principais

- **Tipo**: apenas 2 — Crédito (Entrada) e Débito (Saída)
- **Recorrências** geram transações automaticamente a cada request autenticado
  (via `context_processors.saldos_mensais`), sem Celery/cron. Backfill limitado
  a 3 meses.
- **Transações em cartão** vão sempre para o mês seguinte (`calcular_proxima_fatura`)
- **Parcelas**: geram N transações vinculadas por `grupo_id`; edição/exclusão
  pode aplicar a "todas as parcelas futuras" (cascata opcional pelo usuário)
- **Recorrência excluída** não apaga transações já geradas (preserva histórico)

---

## Segurança

- **Criptografia AES-256** (Fernet) nos campos sensíveis via `encrypted_model_fields`
- **Filtro por `user`** em todas as queries sensíveis (proteção contra IDOR)
- **`@login_required`** em praticamente todas as views
- **`@staff_member_required`** em funções administrativas (gerenciar usuários)
- **`update_session_auth_hash`** chamado ao trocar senha (mantém sessão ativa)

---

## Manual do usuário

Veja [`Manual_do_Usuario.md`](Manual_do_Usuario.md) — guia completo com
capturas de tela das principais telas.

---

## Roadmap / melhorias futuras

- [ ] Configurar DRF com endpoints REST para mobile
- [ ] Importar extrato CSV
- [ ] Categorização automática por título
- [ ] Alertas de metas estouradas por email
- [ ] Exportar PDF do relatório mensal
- [ ] Cache de saldos no context_processor
- [ ] Testes automatizados (não há testes hoje)
- [ ] Configurar SMTP em produção (atualmente `console`)
