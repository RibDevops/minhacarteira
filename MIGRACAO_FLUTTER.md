# Migração Flutter — Minha Carteira Digital
### Documento de acompanhamento (atualizar a cada etapa)

> Enviar este arquivo no início de cada nova conversa + "continue a partir
> daqui". Não pedir para reexplicar decisões já tomadas abaixo.

**Última atualização:** 31/07/2026

---

## Decisões fixadas (não perguntar de novo)
- Web (Django templates) e App (Flutter) rodam **em paralelo**, mesmo backend.
- Auth API: **Token simples do DRF** (não JWT).
- Stack Flutter: dio, go_router, shared_preferences, flutter_secure_storage,
  provider (bloc só se justificar).
- Estrutura: `lib/{models,services,repositories,screens,widgets,providers,utils,theme}/`
- Regra: reaproveitar Django/models/regras de negócio; nunca reescrever
  módulo que já funciona; perguntar antes de decisão ambígua.

---

## Status por etapa

| # | Etapa | Status | Commit/patch |
|---|---|---|---|
| 1 | Analisar estrutura atual / identificar backend | ✅ Concluído | — |
| 2 | API REST (DRF) — base | ✅ Concluído | `f7b6247` |
| 3 | API — Metas | ✅ Concluído | `f7b6247` |
| 4 | API — Recorrências | ✅ Concluído (Manus) | `61066ec` |
| 5 | API — Dashboard/gráficos (endpoint agregado) | ✅ Concluído (Manus) | `61066ec` |
| 6 | Criar projeto Flutter (estrutura de pastas) | ⬜ Pendente | |
| 7 | Camada `services/` (dio) + login | ⬜ Pendente | |
| 8 | Telas: login | ⬜ Pendente | |
| 9 | Telas: lista de transações | ⬜ Pendente | |
| 10 | Telas: registro rápido | ⬜ Pendente | |
| 11 | Telas: dashboard/calendário | ⬜ Pendente | |
| 12 | Telas: cartões/metas/recorrências | ⬜ Pendente | |
| 13 | Navegação (go_router) | ⬜ Pendente | |
| 14 | Build Android (.apk/.aab) | ⬜ Pendente | |
| 15 | Build iOS (.ipa) | ⬜ Pendente | |

---

## Etapa 2 — API base (detalhe)

**Criados:** `cal/api/__init__.py`, `cal/api/serializers.py`, `cal/api/views.py`, `cal/api/urls.py`
**Modificados:** `core/settings.py` (DRF + token auth ativados), `core/urls.py` (`/api/`)

**Endpoints ativos:**
```
POST /api/auth/token/              {username, password} -> {token}
GET/POST      /api/transacoes/     ?mes=X&ano=Y filtra
GET/PUT/DELETE /api/transacoes/{id}/
GET/POST      /api/categorias/
GET/POST      /api/cartoes/
GET           /api/tipos/          (somente leitura, global)
```

Autenticação: header `Authorization: Token <token>`.
Todos os endpoints filtram por `request.user`; categoria/cartão de outro
usuário são rejeitados (400) — mesma regra de segurança das views web.

**Testado:** 22 testes web (sem quebra), obtenção de token, CRUD de
transação, bloqueio de IDOR, 401 sem token.

**Pendente de aplicar no repo real:** rodar
```bash
git apply api_base.patch
python manage.py migrate
python manage.py test cal
git add cal/api/ core/settings.py core/urls.py
git commit -m "feat: API REST base (DRF) para o app Flutter"
git push origin main
```
Confirmar aqui quando aplicado, pra eu marcar como commitado.

---

## Etapa 3 — API Metas (detalhe)

**Modificados:** `cal/api/serializers.py` (+`MetaCategoriaSerializer`),
`cal/api/views.py` (+`MetaCategoriaViewSet`), `cal/api/urls.py` (rota `metas`)

```
GET/POST      /api/metas/        ?mes=X&ano=Y filtra
GET/PUT/DELETE /api/metas/{id}/
```
Mesma validação de categoria-de-outro-usuário da Transação.

**Testado:** criação, filtro por mês/ano, bloqueio de IDOR. 22 testes web OK.

---

## Etapas 4 e 5 — Recorrências + Dashboard agregado (feito pela Manus)

```
GET/POST       /api/recorrencias/
GET/PUT/DELETE /api/recorrencias/{id}/
GET            /api/dashboard/?mes=X&ano=Y
```
`DashboardAPIView` retorna num único payload: saldos do mês, dados dos dois
gráficos (categoria/tipo) e progresso das metas — pensado pra tela inicial
do app não precisar de várias chamadas separadas.

**Validado por mim (Claude):** 22 testes web OK, endpoints testados com
dados reais (token, listagem de recorrências, dashboard com saldos/gráficos/
metas retornando corretamente).

**Pendência de organização:** ver `COORDENACAO_IAS.md` — pasta `manus/` com
cópias redundantes a limpar.

---

## Próximo passo
Etapa 6: criar o projeto Flutter (estrutura de pastas). Aguardando confirmação.
