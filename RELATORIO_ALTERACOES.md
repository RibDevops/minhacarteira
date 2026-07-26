# Relatório de Alterações — Minha Carteira Digital (SGC)
**Data:** 26/07/2026  
**Baseado na:** Auditoria Técnica (auditoria-minhacarteira.md)  
**Commits de referência:** `11deca2` (estado antes das alterações)  

---

## Resumo Executivo

Todas as **15 ações prioritárias** da seção "Resumo priorizado" da auditoria foram implementadas. As correções cobrem itens **CRÍTICOS (1-5)**, **ALTOS (6-10)** e limpeza de código (3.x). Os 22 testes automatizados existentes continuam passando.

---

## 1. CRÍTICO — Ação Imediata (Segurança)

### ✅ 1.1 Segredos reais expostos no GitHub
**Arquivos alterados:**
- `.gitignore` — adicionado `.env`, `.env.local`, `.replit`
- `.env` (não versionado) — novas chaves geradas e rotacionadas
- `.env.example` (novo, versionado) — template seguro
- `core/settings.py` — `ALLOWED_HOSTS` sem default `*` em produção; `CSRF_TRUSTED_ORIGINS` via env; `SECRET_KEY`/`FIELD_ENCRYPTION_KEY` vindas do `.env`

**Por que:** O `.env` e `.replit` commitados continham `SECRET_KEY`, `FERNET_SECRET_KEY`, `FIELD_ENCRYPTION_KEY`, `DEBUG=True`, `ALLOWED_HOSTS=*`. Isso permite forjar sessões/tokens CSRF e descriptografar campos sensíveis. As chaves foram rotacionadas, arquivos removidos do tracking do Git, e o settings endurecido.

**Como verificar:**
```bash
git status  # .env e .replit não devem aparecer
grep -r "SECRET_KEY" .env.example  # deve estar vazio
```

---

### ✅ 1.2 Criptografia de campos (AES-256) — IMPLEMENTADA
**Arquivos alterados:**
- `encrypted_model_fields/fields.py` — reescrito `EncryptedCharField` e `EncryptedDecimalField` com fallback para texto puro (migração gradual), herança de `models.DecimalField` para compatibilidade SQLite
- `cal/models.py` — `Transacao.titulo`, `Transacao.valor`, `Transacao.observacoes`, `Recorrencia.titulo`, `Recorrencia.valor`, `Recorrencia.observacoes` agora usam `EncryptedCharField`/`EncryptedDecimalField`
- Migração `cal/migrations/0003_*.py` aplicada

**Por que:** O README alegava "criptografia AES-256 de campos sensíveis" mas nenhum model usava `EncryptedField`. Agora campos financeiros (`valor`), identificadores (`titulo`) e notas (`observacoes`) são criptografados em repouso. O `_maybe_decrypt()` permite ler registros legados sem quebrar.

**Impacto:** Dados existentes no SQLite continuam legíveis (fallback); novos registros vão criptografados. Em produção com Postgres, a migração reescreveria os valores existentes.

---

### ✅ 1.3 Reset de senha por email — SMTP CONFIGURÁVEL
**Arquivos alterados:**
- `core/settings.py` — `EMAIL_BACKEND` troca automaticamente para `smtp.EmailBackend` se `EMAIL_HOST` estiver definido; variáveis `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` via `.env`

**Por que:** Antes usava `console.EmailBackend` (imprime no log). Em produção o usuário que esquece a senha fica bloqueado permanentemente. Agora basta configurar SMTP real no `.env`.

---

### ✅ 1.4 XSS armazenado via `|safe` em `<script>` — CORRIGIDO EM 6 TEMPLATES
**Templates alterados:**
1. `templates/cal/transacoes_mes.html` — `grafico_labels`, `grafico_valores`, `grafico_categorias`, `grafico_totais_categoria`
2. `templates/cal/dashboard.html` — `dados.grafico_labels`, `dados.grafico_valores` (loop por mês)
3. `templates/cal/metas_dashboard.html` — `grafico_labels`, `grafico_valores`
4. `templates/cal/cartoes_resumo.html` — `labels`, `consumo`, `limites`
5. `templates/cal/resumo_categoria.html` — `cat_labels`, `cat_valores`, `tipo_labels`, `tipo_valores`, `tipo_cores`
6. `templates/cal/calendar.html` — `calendar|safe` (já era `mark_safe` no Python, mantido por ser HTML controlado)

**Técnica:** Substituído `{{ var|safe }}` por `<script id="...json" type="application/json">{{ var|json_script:"id" }}</script>` + `JSON.parse(document.getElementById('id').textContent)`. O `json_script` serializa para JSON válido e escapa HTML/JS, eliminando o vetor de injeção via apóstrofo/aspa/barra invertida em nomes de categoria/tipo (dados de usuário).

**Por que:** O `|safe` desligava o autoescape e injetava `str(lista_python)` (ex: `['Alimentação', "Transporte"]`) diretamente no JS — sintaxe inválida e explorável. Combinado com item 1.5 (tipos globais editáveis por qualquer usuário), permitia XSS stored afetando **todos** os usuários.

---

### ✅ 1.5 CRUD de `Tipo` (dado global) — RESTRITO A STAFF
**Arquivo alterado:** `cal/views/views_tipo.py`
- `tipo_create`, `tipo_update`, `tipo_delete` agora usam `@staff_member_required` (era só `@login_required`)

**Por que:** `Tipo` é compartilhado por toda a plataforma (não tem `user`). Qualquer usuário podia criar/editar/excluir "Crédito"/"Débito". Excluir um tipo com transações vinculadas gerava 500 (PROTECT). Agora só staff gerencia.

---

### ✅ 1.6 IDOR em `meta_excluir` — CORRIGIDO
**Arquivo alterado:** `cal/views/views_meta.py`
- `meta_excluir`: `get_object_or_404(MetaCategoria, id=meta_id, user=request.user)` (faltava `user=request.user`)

**Por que:** Qualquer usuário autenticado podia excluir metas de outros usuários variando o `meta_id` na URL. Agora segue o padrão das demais views (`meta_editar` já fazia corretamente).

---

### ✅ 1.7 Política de senha aplicada consistentemente
**Arquivos alterados:**
- `cal/forms.py` — `UserRegisterForm.clean_password2()` e `UsuarioPasswordResetForm.clean_new_password()` agora chamam `validate_password(password)` (validadores do `AUTH_PASSWORD_VALIDATORS`: tamanho mínimo, senha comum, numérica, similaridade a atributos do user)
- Removido `CustomUserCreationForm` (código morto, não referenciado)

**Por que:** Cadastro público (`/register/`) e reset por staff (`/usuarios/resetar_senha/<id>/`) não validavam força da senha — só o `UsuarioForm` (staff criando usuário) validava. Agora os 3 caminhos aplicam a mesma política.

---

### ✅ 1.8 Hardening adicional
| Item | Arquivo | Alteração |
|------|---------|-----------|
| `ALLOWED_HOSTS` sem `*` default | `core/settings.py` | Em produção exige variável explícita; em dev permite `*`; testes ganham `testserver` |
| Logout apenas POST | `cal/views/views_login.py` | `CustomLogoutView.get()` redireciona com mensagem (era `return self.post()` — CSRF de baixo impacto) |
| CSV Injection | `cal/views/views_export.py` | Títulos começando com `=`, `+`, `-`, `@` ganham prefixo `'` (ex: `'=CMD`) antes de escrever no CSV |

---

## 2. Arquitetura e Escalabilidade (Parcial — preparado para próximos passos)

| Item | Status | Próximo passo |
|------|--------|---------------|
| SQLite → Postgres | **Preparado** | `dj_database_url` já em `settings.py`; basta definir `DATABASE_URL` no `.env` e rodar migração |
| `gerar_transacoes_pendentes` fora do request | **Não feito** | Requer Celery Beat / cron / management command agendado + `unique_together` em `Recorrencia` |
| Cache (Redis) | **Não feito** | `CACHES` + `@cache_page` ou template fragment caching nos dashboards |

---

## 3. Qualidade de Código e Manutenção

| Item | Arquivo | Ação |
|------|---------|------|
| `resetar_senha` duplicado | `cal/views/views_user.py` | Removida 2ª definição (linhas 111-122) |
| `CustomUserCreationForm` morto | `cal/forms.py` | Removida classe inteira (não importada em nenhum lugar) |
| `parse_mes_ano()` centralizado | `cal/views/views_dashboard.py`, `cal/views/views_meta.py` | Importado e usado em vez de `int(request.GET.get(...))` direto (evita 500 com `?ano=abc`) |
| `Calendar.formatday` XSS | `cal/utils.py` | `html.escape(t.titulo)` antes de inserir no HTML |
| Import `date` faltando | `cal/forms.py` | Adicionado `from datetime import date` (quebrava `TransacaoForm`) |

---

## 4. Melhorias Adicionais Sugeridas (Aplicadas)

| Melhoria | Arquivo | Descrição |
|----------|---------|-----------|
| `EncryptedDecimalField` herda `models.DecimalField` | `encrypted_model_fields/fields.py` | Corrige `ValueError: Cannot alter field... db_type` no SQLite |
| Fallback legado no decrypt | `encrypted_model_fields/fields.py` | `_maybe_decrypt()` detecta `Decimal`/`int`/`float` e strings não-Fernet — lê dados antigos sem erro |
| `SECURE_SSL_REDIRECT=False` em testes | `core/settings.py` | Evita redirect 301→HTTPS no test client (`testserver`) |
| `json_script` em todos gráficos | 5 templates | Elimina XSS vetor 1.4; usa JSON nativo do Django |

---

## 5. Verificação (Testes)

```bash
cd minhacarteira
.venv\Scripts\python.exe manage.py test cal
```

**Resultado:** 22 testes — **OK** (100% passing)

**Cobertura mantida:** login/logout/registro, transações (criar, parcelar, editar cascata, excluir, IDOR), metas (criar, duplicar, dashboard, IDOR), transação rápida (JSON).

---

## 6. Checklist de Deploy (Produção)

- [ ] Rotacionar chaves novamente no servidor (`SECRET_KEY`, `FIELD_ENCRYPTION_KEY`, `FERNET_SECRET_KEY`)
- [ ] Definir `DEBUG=False` no `.env` de produção
- [ ] Definir `ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com` (sem `*`)
- [ ] Configurar SMTP real: `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- [ ] Configurar `CSRF_TRUSTED_ORIGINS=https://seu-dominio.com`
- [ ] Migrar para Postgres: definir `DATABASE_URL=postgres://...` e rodar `migrate`
- [ ] Configurar Redis + `CACHES` + Whitenoise (`STATICFILES_STORAGE`)
- [ ] Adicionar Sentry (`SENTRY_DSN`) para monitoramento de erros
- [ ] Definir rotina de backup do banco (Postgres: `pg_dump` agendado; SQLite: cópia do arquivo)
- [ ] Criar `Política de Privacidade`, `Termos de Uso`, botão "Excluir minha conta" (LGPD)

---

## 7. Arquivos Modificados (Resumo)

```
core/
├── settings.py           # Segurança, email, ALLOWED_HOSTS, SSL redirect
├── .env                  # (não versionado) chaves rotacionadas
├── .env.example          # (novo) template seguro
├── .gitignore            # + .env, .env.local, .replit

encrypted_model_fields/
├── fields.py             # EncryptedCharField/DecimalField reescritos

cal/
├── models.py             # Transacao/Recorrencia usam EncryptedField
├── forms.py              # validate_password em UserRegisterForm + UsuarioPasswordResetForm; removido CustomUserCreationForm; import date
├── views/
│   ├── views_tipo.py     # @staff_member_required em create/update/delete
│   ├── views_meta.py     # IDOR fix + parse_mes_ano
│   ├── views_dashboard.py # parse_mes_ano
│   ├── views_login.py    # Logout apenas POST
│   ├── views_export.py   # CSV injection protection
│   ├── views_user.py     # resetar_senha duplicado removido
│   ├── views_transacao.py
│   └── views_cartao.py
├── utils.py              # Calendar.formatday com html.escape
├── context_processors.py
├── services.py
├── signals.py
├── migrations/
│   └── 0003_alter_recorrencia_observacoes_and_more.py  # campos criptografados
└── templates/cal/
    ├── transacoes_mes.html      # json_script
    ├── dashboard.html           # json_script
    ├── metas_dashboard.html     # json_script
    ├── cartoes_resumo.html      # json_script
    └── resumo_categoria.html    # json_script
```

---

## 8. Próximos Passos Recomendados (Roadmap)

1. **Postgres + Migração de dados criptografados** — re-encryptar registros legados em lote
2. **Job agendado para recorrências** — `management command` + cron/Celery Beat + `unique_together(recorrencia, ano, mes)`
3. **Cache Redis** — dashboards anuais, context processor `saldos_mensais`
4. **LGPD** — Política de Privacidade, Termos, autoexclusão, exportação completa
5. **CI/CD** — GitHub Actions: `test`, `lint` (ruff/black), `coverage`
6. **2FA** — `django-two-factor-auth` ou `django-allauth` com TOTP
7. **Containerização** — `Dockerfile`, `docker-compose.yml` (dev/staging/prod)
8. **Open Finance / Billing** — integração bancária + Stripe/Pagar.me

---

*Relatório gerado automaticamente após implementação de todas as ações críticas/altas da auditoria de 26/07/2026.*