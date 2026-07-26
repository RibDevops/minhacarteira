# Auditoria Técnica — Minha Carteira Digital (SGC)
**Repositório:** github.com/RibDevops/minhacarteira · **Data da leitura:** 26/07/2026
**Stack:** Django 5.2.10, SQLite, Bootstrap 5, Chart.js, Replit (deploy)

Este documento é apenas leitura/registro — nenhuma alteração foi aplicada ao código. É organizado por prioridade: comece pela seção 1 (ação imediata), depois use as demais como roadmap.

---

## 1. CRÍTICO — Ação imediata (segurança)

### 1.1. Segredos reais expostos publicamente no GitHub
O repositório é **público**, e dois arquivos commitados contêm segredos reais em texto puro:

- **`.env`** (rastreado pelo Git mesmo estando listado no `.gitignore` — foi commitado antes de ser ignorado): `SECRET_KEY`, `FERNET_SECRET_KEY`, `FIELD_ENCRYPTION_KEY`, `DEBUG`, `ALLOWED_HOSTS`.
- **`.replit`**, seção `[userenv.shared]`: os mesmos valores reais, incluindo `DEBUG = "True"` e `ALLOWED_HOSTS = "*"`.

**Por que isso é grave:** o `SECRET_KEY` do Django assina cookies de sessão, tokens de CSRF e tokens de reset de senha. Qualquer pessoa com esse valor pode, em tese, forjar sessões/tokens e potencialmente assumir contas — incluindo contas de staff. O `FIELD_ENCRYPTION_KEY` é a chave de criptografia de campos sensíveis (ver 1.2). Isso está no histórico do Git há pelo menos 7 commits, então mesmo apagando o arquivo agora os valores continuam recuperáveis no histórico.

**O que fazer:**
- Rotacionar imediatamente `SECRET_KEY` e `FIELD_ENCRYPTION_KEY`/`FERNET_SECRET_KEY` em produção.
- Remover `.env` e `.replit` do rastreamento do Git e reescrever o histórico (`git filter-repo` ou BFG) para apagar os valores dos commits antigos — ou, se não for viável, tratar os valores como definitivamente comprometidos e assumir que precisam ser trocados de qualquer forma.
- Nunca versionar `[userenv.shared]` do Replit com valores reais — usar o painel de "Secrets" do Replit (que não vai para o Git).
- Definir `DEBUG=False` e `ALLOWED_HOSTS` explícito (não `*`) como valor padrão em qualquer ambiente publicado.

### 1.2. Criptografia de campos anunciada no README, mas não implementada
O `readme.md` afirma: *"Desenvolvido com criptografia AES-256 de campos sensíveis"* e lista isso na seção "Segurança". Na prática:
- A dependência `encrypted_model_fields` está instalada e configurada (`FIELD_ENCRYPTION_KEY` existe em `settings.py`), **mas nenhum campo de nenhum model usa `EncryptedField`** — busquei em todo o projeto e o único uso da lib é o `INSTALLED_APPS`.
- Ou seja: valores de transações, títulos, observações — tudo trafega e é armazenado em texto puro no SQLite.

Isso é uma divergência entre o que é comunicado ao usuário/investidor e o que o código realmente faz. Antes de comercializar, é preciso decidir: implementar a criptografia de fato nos campos sensíveis (`valor`, `titulo`, `observacoes`), ou ajustar a documentação para não alegar uma proteção que não existe. Para um produto financeiro, essa é uma questão de confiança e, dependendo de como for comercializado, de responsabilidade legal.

### 1.3. Reset de senha por email não funciona em produção
`EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` — isso faz o Django **imprimir o email no console/log em vez de enviá-lo**. O fluxo de "esqueci minha senha" (que existe e está bem implementado nas URLs) não entrega o link a usuários reais hoje. É preciso configurar um backend SMTP real (SendGrid, Amazon SES, Mailgun, Postmark etc.) antes do lançamento comercial — sem isso, qualquer usuário que esquecer a senha fica bloqueado permanentemente.

### 1.4. XSS armazenado via `|safe` em listas Python injetadas em `<script>`
Este é o achado mais sério de segurança no código de aplicação. Em pelo menos 6 templates (`transacoes_mes.html`, `dashboard.html`, `cartoes_resumo.html`, `resumo_categoria.html`, `metas_dashboard.html`, e o padrão se repete), listas Python de strings (nomes de categoria, descrição de tipo) são injetadas diretamente em blocos `<script>` assim:

```
labels: {{ grafico_labels|safe }},
```

O filtro `|safe` desliga o autoescape do Django, e o valor inserido é o `str()` de uma lista Python (ex.: `['Alimentação', 'Transporte']`), **não** um JSON válido/seguro para JavaScript. Como esses nomes vêm de texto livre digitado pelo usuário (nome de categoria, descrição de "Tipo"), um apóstrofo, aspas ou barra invertida no nome já quebra a sintaxe do array — e um valor elaborado de propósito permite escapar do literal e executar JavaScript arbitrário no navegador de quem visualizar aquele gráfico.

**Agravante:** o model `Tipo` (usado em `tipo__descricao`, uma das listas afetadas) é **global** — compartilhado por todos os usuários da plataforma (não tem campo `user`). Combinado com o próximo achado (1.5), isso significa que qualquer usuário autenticado comum consegue, hoje, plantar um payload que executa no navegador de **todos os outros usuários** que abrirem a tela de transações do mês.

**Direção da correção:** parar de fazer interpolação manual de listas Python em JS. Usar o filtro nativo `json_script` do Django (`{{ lista|json_script:"algum-id" }}` + `JSON.parse(document.getElementById(...).textContent)` no JS) ou passar os dados já serializados com `json.dumps()` da view, envolvidos em `mark_safe` só depois de serializados corretamente — nunca `str(lista)|safe`.

### 1.5. Controle de acesso quebrado no CRUD de "Tipo" (dado global)
Em `cal/views/views_tipo.py`, as views `tipo_create`, `tipo_update` e `tipo_delete` exigem apenas `@login_required` — **qualquer usuário logado**, não só staff, pode criar, editar ou excluir os registros de `Tipo` (Crédito/Débito), que são compartilhados por toda a base de usuários. Os comentários no próprio código ("Removido o filtro por usuário", "tipos são globais") indicam que essa restrição foi removida propositalmente em algum momento, sem adicionar um controle equivalente de "só staff".

Consequências práticas:
- Combinado com 1.4, é o vetor que permite XSS afetando todos os usuários.
- Qualquer usuário pode excluir o tipo "Débito" ou "Crédito" usado pela aplicação inteira. Como `Transacao.tipo` usa `on_delete=PROTECT`, isso geraria uma página de erro 500 não tratada assim que houvesse qualquer transação vinculada — na melhor hipótese quebra a experiência, na pior derruba a tela pra todo mundo até um admin perceber.

**Correção:** restringir essas três views com `@staff_member_required` (ou equivalente), já que `Tipo` é configuração de plataforma, não dado de usuário.

### 1.6. IDOR em exclusão de meta (`meta_excluir`)
Em `cal/views/views_meta.py`, `meta_excluir` busca o objeto assim:
```
meta = get_object_or_404(MetaCategoria, id=meta_id)
```
sem filtrar por `user=request.user` — diferente de todas as outras views de meta (`meta_editar`, que faz isso corretamente). Isso é uma falha clássica de IDOR (Insecure Direct Object Reference): qualquer usuário autenticado, apenas variando o `meta_id` na URL, consegue excluir a meta de orçamento de **qualquer outro usuário** da plataforma.

### 1.7. Política de senha não é aplicada de forma consistente
`settings.py` define `AUTH_PASSWORD_VALIDATORS` (tamanho mínimo, senha comum, etc.), mas esses validadores só são chamados automaticamente pelos formulários nativos do Django (`UserCreationForm`, `PasswordChangeForm`, `SetPasswordForm`). No app:
- `UserRegisterForm` (usado no cadastro público, `/register/`) é um `forms.ModelForm` simples que só confere se as duas senhas digitadas são iguais — **não chama `validate_password()`**. Ou seja, qualquer usuário pode se cadastrar publicamente com senha "123" ou "aaaa", sem qualquer validação de força.
- `UsuarioPasswordResetForm` (usado por staff para resetar senha de outro usuário, em `resetar_senha`) também não valida força de senha.
- Em contraste, `UsuarioForm` (herda de `UserCreationForm`, usado por staff ao criar um usuário novo) valida corretamente.

Ou seja: a política de senha declarada no settings só protege 1 de 3 caminhos possíveis de definição de senha.

### 1.8. Outros detalhes de hardening
- `ALLOWED_HOSTS` tem default `'*'` no código (`config('ALLOWED_HOSTS', default='*', ...)`) — se a variável de ambiente não for definida em algum ambiente, a proteção contra Host header attacks fica desativada silenciosamente.
- `CSRF_TRUSTED_ORIGINS` está hardcoded para `*.replit.dev` e `*.repl.co` — amarra a configuração de segurança a um provedor específico; ao migrar de hospedagem isso precisa ser lembrado manualmente.
- `CustomLogoutView` aceita logout via `GET` (reencaminha `get` para `post`) — o Django recomenda logout só via POST justamente para evitar que um link/imagem de terceiros desloguem o usuário sem consentimento (CSRF de baixo impacto, mas é o tipo de detalhe que auditorias de segurança cobram).
- Exportação de CSV (`exportar_transacoes_csv`) grava `titulo` do usuário sem neutralizar caracteres como `=`, `+`, `-`, `@` no início da célula — isso é a base de "CSV Injection": se o título de uma transação começar com uma fórmula do Excel, ela pode ser executada ao abrir o CSV exportado.

---

## 2. Arquitetura e escalabilidade

### 2.1. SQLite em produção
O banco de dados é SQLite (`db.sqlite3`), inclusive em produção (não há configuração de Postgres/MySQL apesar de `dj-database-url` já estar instalado, pronto para uma `DATABASE_URL`). SQLite trava em escrita concorrente (um único writer por vez) e não escala horizontalmente. Para uma aplicação comercial com múltiplos usuários simultâneos, migrar para Postgres (mesmo que gerenciado, tipo Neon/Supabase/RDS) é praticamente pré-requisito — e a infraestrutura para isso (`dj_database_url`) já está no projeto, só não está sendo usada.

### 2.2. Geração de recorrências síncrona, a cada request
`gerar_transacoes_pendentes(user)` é chamada dentro do `context_processor` `saldos_mensais`, que roda em **toda página renderizada por um usuário autenticado** — não só nas telas relacionadas a recorrência. A cada request ela:
- Itera todas as recorrências ativas do usuário;
- Para cada uma, faz um laço mês a mês (até 3 meses de backfill) com uma query `.exists()` por mês para checar se já foi gerada.

Isso significa dezenas de queries extras em **toda** navegação da pessoa pelo sistema, mesmo em páginas que não têm nada a ver com recorrência (editar uma categoria, ver um cartão, etc.). Além do custo de performance, existe uma condição de corrida real: o check-then-create (`if not ja_existe: Transacao.objects.create(...)`) não é atômico, e não há `unique_together` no banco garantindo isso — duas abas abertas ao mesmo tempo, ou dois requests simultâneos, podem gerar a mesma transação de recorrência duplicada.

**Direção de melhoria:** mover a geração de recorrências para fora do ciclo de request — um job agendado (cron, Celery Beat, ou mesmo uma tarefa disparada 1x/dia) — e adicionar uma constraint única no banco (`unique_together` em `recorrencia` + ano + mês) como rede de segurança contra duplicidade.

### 2.3. Context processor global carrega dados que a maioria das páginas não precisa
O mesmo `saldos_mensais` roda em toda página e sempre calcula saldo do mês atual **e** do próximo (múltiplos aggregates), busca categorias, tipos e cartões do usuário (para o modal de Registro Rápido, que só existe na navbar). Isso é aceitável em baixa escala, mas é over-fetching sistemático: toda tela paga o custo de dados que só a navbar/modal usam. Vale considerar mover esses dados para uma chamada assíncrona (endpoint JSON chamado 1x ao carregar a página, com cache de alguns minutos) em vez de recalcular em cada render no servidor.

### 2.4. Ausência de camada de cache
Não há Redis/Memcached configurado. Dashboards anuais (`detalhe_mensal_ano`, que roda 12 sub-consultas agregadas por ano visualizado) e o context processor de saldo seriam bons candidatos a cache de curta duração (poucos minutos), reduzindo carga de banco à medida que a base de usuários cresce.

---

## 3. Qualidade de código e manutenção

- **Função duplicada:** `resetar_senha` está definida duas vezes em `views_user.py` (linhas ~63 e ~111), idêntica nas duas — a segunda sobrescreve silenciosamente a primeira. Não quebra nada hoje, mas é sinal de código não revisado/merge malfeito.
- **Formulários de usuário redundantes:** `UserRegisterForm`, `CustomUserCreationForm` e `UsuarioForm` fazem essencialmente a mesma coisa (criar usuário com senha) com pequenas variações; `CustomUserCreationForm` é código morto — não é referenciado em nenhum lugar do projeto além da própria definição.
- **Duas lógicas paralelas de categorias padrão:** `register_view` cria uma lista fixa de 9 categorias na mão, e separadamente `signals.py` (`create_user_categories`) copia qualquer `Categoria` com `is_global=True` para todo usuário novo via `post_save` do `User`. Hoje isso não duplica nada porque nenhuma categoria tem `is_global=True` ativada em uso normal (a fixture `categorias_gastos.json` existe mas não há indício de que seja carregada em algum setup documentado) — mas são dois mecanismos concorrentes para o mesmo problema, e assim que uma categoria global for ativada (via shell ou futura tela de admin), usuários novos ganhariam categorias duplicadas.
- **Uso inconsistente do utilitário de parsing de mês/ano:** `cal/utils.py` tem `parse_mes_ano(request)`, feito especificamente para não deixar a aplicação quebrar com `?mes=abc` ou `?ano=xyz` na URL. Mas `views_dashboard.dashboard` e `views_meta.metas_dashboard` não usam essa função — fazem `int(request.GET.get('ano', hoje.year))` direto, sem `try/except`. Um usuário (ou bot) acessando `/dashboard/?ano=abc` hoje derruba a página com erro 500.
- **Geração manual de HTML sem escape** em `cal.utils.Calendar.formatday` (usado no calendário mensal): a string do título da transação é inserida via f-string diretamente no HTML que depois é marcado como `mark_safe`, reforçando a mesma classe de problema do item 1.4, dessa vez no calendário.
- **Dependência instalada e não utilizada:** Django REST Framework está em `requirements.txt` mas não há nenhuma `APIView`/serializer no projeto (o próprio README já reconhece isso). Se não há plano de API por trás do produto, vale remover para reduzir superfície; se há plano de app mobile/nativo futuro, vale já estruturar.

---

## 4. Testes e CI/CD

- Existem hoje **22 testes automatizados** (`test_auth.py`, `test_metas.py`, `test_transacao.py` — 442 linhas no total), cobrindo login/logout/registro, metas e transações básicas.
- **Não há teste nenhum** para: cartões, categorias, recorrências, dashboard anual, exportação CSV, calendário, ou qualquer um dos problemas de segurança listados na seção 1 (nenhum teste de IDOR, nenhum teste de escapamento de HTML/JS, nenhum teste de permissão em `views_tipo`).
- Não há nenhuma configuração de CI (nenhum workflow do GitHub Actions, nenhum `tox.ini`/`pytest.ini`) — os testes existentes só rodam se alguém lembrar de rodá-los manualmente antes de um push. Não há medição de cobertura (`coverage.py`).
- Não há lint/formatação automatizada (flake8, black, isort, ruff) nem pre-commit hooks — o que explica achados como a função duplicada e o `}` sobrando no CSS (já corrigido na conversa anterior).

Para um produto comercial, o mínimo recomendável é: um workflow de CI que rode os testes e um linter a cada push/PR, e cobertura de teste específica para as rotas sensíveis (qualquer view que faça `get_object_or_404` deveria ter um teste garantindo que o usuário A não acessa/edita/exclui dado do usuário B).

---

## 5. DevOps e infraestrutura

- **Acoplamento ao Replit:** `CSRF_TRUSTED_ORIGINS` fixo para domínios do Replit, e todo o fluxo de deploy (`.replit`) está desenhado para essa plataforma especificamente. Migrar para outro provedor exigiria reescrever essa parte do settings e do processo de deploy.
- **Sem containerização:** não há `Dockerfile`/`docker-compose.yml`. Isso dificulta rodar o projeto de forma idêntica em dev/staging/produção e dificulta a portabilidade para qualquer nuvem fora do Replit.
- **Sem separação clara de settings por ambiente:** um único `settings.py` alterna comportamento via `if not DEBUG`. Funciona, mas projetos comerciais normalmente se beneficiam de `settings/base.py` + `settings/dev.py` + `settings/prod.py`, deixando explícito o que muda entre ambientes.
- **Arquivos estáticos:** não há Whitenoise nem storage externo (S3/Cloud Storage) configurado para servir `STATIC_ROOT`/`MEDIA_ROOT` em produção — hoje depende inteiramente de como o Replit serve esses arquivos por fora do Django.
- **Sem monitoramento de erros:** não há Sentry (ou similar) integrado. Hoje, um erro em produção só aparece no `logs/django.log` local do servidor — ninguém é alertado ativamente.
- **Backup do banco:** não há menção de rotina de backup do SQLite (nem, mais adiante, do futuro Postgres). Para um app financeiro, isso é essencial antes de ter usuários reais dependendo dos dados.

---

## 6. Conformidade legal (LGPD) e confiança do usuário

Como é um produto de finanças pessoais em português, mirando o mercado brasileiro, a Lei Geral de Proteção de Dados (LGPD) é diretamente aplicável assim que houver comercialização:

- **Não há Política de Privacidade nem Termos de Uso** em nenhuma página do site (busquei em todos os templates).
- **Não há aviso/consentimento de cookies.**
- **Não há mecanismo de autoatendimento para o titular dos dados** solicitar exclusão da própria conta e dados (hoje `excluir_usuario` só existe para staff, um usuário comum não consegue se autoexcluir — direito de eliminação previsto na LGPD).
- **Não há exportação completa dos dados pessoais** (a exportação CSV existe só para transações do mês, não cobre o conceito de portabilidade de dados completo).
- Como comentado em 1.2, **a alegação de criptografia AES-256 no README não corresponde à implementação atual** — isso é particularmente sensível num contexto de compliance, onde alegar uma proteção técnica que não existe pode gerar responsabilidade caso haja um incidente.

Nenhum desses pontos bloqueia o funcionamento técnico do sistema, mas todos são pré-requisitos comuns para comercializar legalmente um produto financeiro no Brasil.

---

## 7. Produto / UX rumo a uma aplicação "de ponta"

Pontos que hoje limitam o produto frente a concorrentes estabelecidos (Mobills, Organizze, Guiabolso/consumo bancário, etc.):

- **Sem autenticação de dois fatores (2FA)** — esperado em qualquer app que lida com dados financeiros.
- **Sem notificações** (email/push) quando uma meta de categoria é estourada, ou quando uma recorrência está prestes a ser cobrada — hoje o usuário só descobre entrando no app e olhando o dashboard de metas.
- **Sem Open Finance / importação automática de extrato bancário** — hoje todo lançamento é manual. Esse costuma ser o principal diferencial competitivo de apps de finanças pessoais modernos no Brasil.
- **Sem compartilhamento familiar/organizacional real** — existe um painel de "usuários" controlado por staff, mas não existe o conceito de "carteira compartilhada" onde duas pessoas (ex.: casal) veem e lançam nas mesmas transações com uma conta cada.
- **PWA implementado, mas com uma falha de estratégia de cache:** o `service worker` (`static/sw.js`) usa cache-first (`caches.match(...).then(response => response || fetch(...))`) inclusive para a rota `/` (a home autenticada). Isso significa que, num dispositivo compartilhado, a página pode ser servida do cache do navegador antes de bater no servidor — arriscando mostrar dados desatualizados ou, em cenários de troca de usuário no mesmo navegador, conteúdo em cache da sessão anterior. Vale revisar para uma estratégia "network-first" nas rotas autenticadas, reservando cache-first só para ativos estáticos (CSS/JS/ícones).
- **Sem gateway de pagamento/assinatura** — se o plano é cobrar pelo produto (freemium, plano pago, etc.), não há nenhuma integração de billing (Stripe, Pagar.me, Mercado Pago) ainda.
- **Multi-idioma/multi-moeda:** hoje fixo em `pt-br` e implicitamente em Real (R$, formatação brasileira hardcoded em vários lugares) — adequado para o mercado atual, mas é uma limitação conhecida caso haja intenção de expandir.

### Pontos fortes que já existem (vale preservar e construir em cima)
- Camada de serviço (`services.py`) bem isolada, com boas queries agregadas via SQL (`Sum`, `select_related`) em vez de somar em Python — mostra preocupação real com performance em pontos-chave.
- Proteção de IDOR feita corretamente e **documentada explicitamente em comentário** na maior parte das views de transação, cartão, categoria e recorrência (a view de metas e a de tipos são as exceções, ver seção 1).
- Testes automatizados já existem para os fluxos mais críticos (login, registro, metas, transação) — falta ampliar, não começar do zero.
- Dark mode já implementado no CSS.
- PWA com manifest e ícones já configurados.
- Documentação interna extensa e bem escrita (comentários explicando o "porquê", não só o "o quê" — isso é raro e valioso para manutenção futura).

---

## 8. Resumo priorizado — por onde começar

| # | Item | Categoria | Urgência |
|---|---|---|---|
| 1 | Rotacionar `SECRET_KEY`/`FIELD_ENCRYPTION_KEY` e limpar histórico do Git | Segurança | Imediata |
| 2 | Corrigir `|safe` + lista Python em `<script>` (XSS, 6 templates) | Segurança | Imediata |
| 3 | Restringir `views_tipo.py` a staff | Segurança | Imediata |
| 4 | Corrigir IDOR em `meta_excluir` | Segurança | Imediata |
| 5 | Configurar envio real de email (reset de senha) | Funcional/Segurança | Imediata |
| 6 | Decidir: implementar criptografia de campo de verdade, ou corrigir o README | Confiança/Legal | Alta |
| 7 | Aplicar `validate_password()` no cadastro público e no reset por staff | Segurança | Alta |
| 8 | Migrar SQLite → Postgres | Arquitetura | Alta (antes de escalar usuários) |
| 9 | Mover geração de recorrências para job agendado, fora do request | Arquitetura | Alta |
| 10 | Política de Privacidade, Termos de Uso, autoexclusão de conta (LGPD) | Legal | Alta (antes de cobrar/comercializar) |
| 11 | CI com testes + lint automático | Qualidade | Média |
| 12 | Ampliar testes (cartão, categoria, recorrência, permissões) | Qualidade | Média |
| 13 | Sentry/monitoramento + estratégia de backup do banco | DevOps | Média |
| 14 | Limpeza de código morto/duplicado (forms, `resetar_senha`, categorias padrão) | Manutenção | Baixa |
| 15 | 2FA, notificações, Open Finance, billing | Produto | Roadmap de médio/longo prazo |

---

*Este relatório reflete o estado do repositório em 26/07/2026 (branch `main`, commit mais recente `11deca2` no momento da leitura). Nenhum arquivo do projeto foi alterado durante esta análise.*
