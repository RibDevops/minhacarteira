# Auditoria de Melhorias — Minha Carteira Digital
### Estado em 30/07/2026, após commit `fbe589f` + correções desta sessão

> Este arquivo é complementar ao `ALTERACOES_PENDENTES.md` (histórico de
> sessões). Este aqui é uma **auditoria de estado atual**: o que existe hoje
> no código e o que vale a pena melhorar, priorizado. Marque os itens com
> [x] conforme forem resolvidos e me envie de volta pra eu continuar.

---

## ✅ Corrigido nesta sessão

- [x] Gráfico "Resumo por Tipo" removido de `/transacoes/` (redundante com os
      cards de totais logo acima)
- [x] Link "Detalhes do Mês" em `/dashboard/` corrigido — antes caía sempre
      no mês atual porque o redirect de `/transacoes-mes/` não preservava
      `?mes=X&ano=Y`; agora aponta direto pra `/transacoes/` com os
      parâmetros certos, e o redirect também foi corrigido como reforço.

---

## 🔴 Prioridade alta

### 1. CSS morto ainda presente (nenhum trabalho de design sobreviveu à troca de repositório)
`static/css/` ainda tem `all.css` (Font Awesome completo, ~5.000 linhas, **zero
classes `fa-` usadas** em qualquer template — o app inteiro usa Bootstrap
Icons), `calendar.css` e `simple-sidebar.css` (nunca carregados em nenhum
template) e `fontawesome.min.css` (idem, 0 usos). Isso é peso morto em todo
carregamento de página.

**Também:** `.btn-fab` está definido em **4 lugares diferentes** (`calendar.css`,
`custom.css`, `fab.css`, e inline em `base.html`) — cada um pode divergir do
outro sem ninguém perceber.

**Ação sugerida:** remover os 4 arquivos não utilizados, consolidar `.btn-fab`
num só lugar. (Eu já tinha essa correção pronta de uma sessão anterior, mas
não sobreviveu à substituição do repositório — posso reaplicar.)

### 2. Tela de login sem nenhum estilo
`templates/registration/login.html` usa a classe `.form-login-container`, que
**não existe em nenhum arquivo CSS do projeto**. A primeira tela que qualquer
pessoa vê ao abrir o app está rodando só com HTML cru do navegador — sem
card, sem centralização, sem identidade visual. (Também já tinha essa
correção pronta antes; não sobreviveu.)

### 3. `staticfiles/` versionado no Git (142 arquivos)
A pasta `staticfiles/` é o **output gerado** por `collectstatic` — não deveria
estar no controle de versão (o próprio `settings.py` já define `STATIC_ROOT`
apontando pra ela, sinal de que é pra ser gerada, não commitada). Isso infla
o repositório e pode ficar dessincronizada do código-fonte real sem ninguém
perceber (alguém edita `static/css/x.css` mas esquece de rodar
`collectstatic` de novo, e o site continua servindo a versão velha).

**Ação sugerida:** adicionar `staticfiles/` ao `.gitignore`, remover do
tracking (`git rm -r --cached staticfiles/`), e rodar `collectstatic` como
parte do processo de deploy (o PythonAnywhere tem essa opção no painel).

### 4. Views duplicadas (função antiga + Class-Based View convivendo)
`cal/views/views_transacao.py` ainda tem `excluir_transacao` e `transacao_view`
— **nenhuma das duas está ligada a nenhuma URL** (confirmei: 0 ocorrências em
`urls.py`). São sobras da migração para Class-Based Views (`views_cbv.py`),
que é quem realmente atende essas rotas hoje. Código morto assim confunde
quem for mexer no projeto depois (parece que faz algo, mas não faz nada).

**Ação sugerida:** remover as funções não utilizadas, ou se alguma ainda for
necessária como referência, mover para um arquivo `_legado.py` com um
comentário explicando por quê.

---

## 🟡 Prioridade média

### 5. Cobertura de testes incompleta
Existem testes só para `test_auth.py`, `test_metas.py` e `test_transacao.py`.
**Sem nenhum teste** para: Categoria (CRUD), Cartão (CRUD), **Recorrência**
(a funcionalidade que teve 3 tentativas de correção de bug recentemente —
seria o primeiro lugar pra testar), dashboard/gráficos, exportação CSV,
registro rápido via modal.

**Ação sugerida:** priorizar teste de Recorrência primeiro (área mais
instável ultimamente), depois Cartão/Categoria.

### 6. Sem CI/CD
Não existe `.github/workflows/`. Cada correção depende de rodar os testes
manualmente antes do push — o que já causou pelo menos um caso nesta sessão
(a correção do dashboard que reabriu uma vulnerabilidade de XSS foi commitada
sem os testes serem rodados antes). Um workflow simples que roda
`manage.py test` a cada push pegaria isso automaticamente.

**Ação sugerida:** um `.github/workflows/tests.yml` básico (instala
dependências, roda `manage.py test`) — não precisa de nada elaborado pra já
ajudar bastante.

### 7. LGPD: sem política de privacidade nem exportação/exclusão de conta visível
Não encontrei página de Política de Privacidade ou Termos de Uso. Há alguma
função de exportação/exclusão em `views_user.py`, mas não confirmei se está
acessível pela interface (link em algum menu) ou só existe no código.

**Ação sugerida:** confirmar se o fluxo de exportar/excluir dados está
acessível pro usuário final, e adicionar uma página simples de política de
privacidade — importante já que o projeto tem esse objetivo desde o início
(mencionado no planejamento original) e será comercializado.

### 8. Paleta de gráficos inconsistente entre páginas
Cada template com gráfico (`dashboard.html`, `lista_transacoes.html`,
`cartoes_resumo.html`, `metas_dashboard.html`) declara seu próprio array de
cores Chart.js na mão. Um gasto de "Alimentação" pode aparecer verde num
gráfico e azul em outro, dependendo da página.

**Ação sugerida:** um arquivo `static/js/charts-theme.js` com uma paleta
única, compartilhada — já cheguei a implementar isso numa sessão anterior,
posso trazer de volta.

---

## 🟢 Prioridade baixa / nice-to-have

### 9. `resumo_categorias_e_tipos()` calcula dados que nem sempre são usados
Depois da remoção do gráfico "por tipo" em `/transacoes/`, o service ainda
calcula `tipo_labels`/`tipo_valores`/`tipo_cores` sempre, mesmo que só
`cat_labels`/`cat_valores` sejam usados ali. Não é um bug, só processamento
desnecessário — pequeno, mas fácil de limpar.

### 10. Import não utilizado em `views_cartao.py`
`resumo_categorias_e_tipos` ainda é importado em `views_cartao.py`, mas a
função que o usava (`resumo_categoria_view`) virou um redirect simples e não
chama mais o service. Import órfão, sem efeito prático, só ruído.

### 11. Sem gunicorn/whitenoise no `requirements.txt`
Não é urgente porque o deploy atual é no PythonAnywhere (que tem WSGI e
serving de estático próprios), mas se algum dia migrar pra outro provedor
(Railway, Render, etc.), vai precisar disso. Só uma nota pro futuro.

### 12. Modal de registro rápido: confirmar se o "modo avançado" (cartão/parcelas) sobreviveu
Confirmei que o modal existe (`modalRegistroRapido` presente em `base.html`),
mas não testei se o `<select>` de cartão e o campo de parcelas dentro dele
ainda funcionam da forma que foi implementada antes — vale um teste rápido
na próxima sessão.

---

## 📋 Como priorizar a partir daqui

Se quiser ir por ordem de "menor esforço, maior ganho de confiança":
1. Item 3 (parar de versionar `staticfiles/`) — 5 minutos, evita bug de cache no futuro
2. Item 6 (CI básico) — evita que um bug de segurança volte a ser commitado sem teste, como aconteceu com o dashboard
3. Item 5 (testes de Recorrência) — é a área que mais teve idas e vindas recentemente
4. Itens 1 e 2 (CSS morto + login sem estilo) — cosmético, mas rápido de reaplicar já que eu tinha isso pronto antes
5. Item 4 (remover views mortas) — limpeza, sem risco
6. Item 7 (LGPD) — mais trabalho, mas importante pra comercialização

Me diz por qual quer que eu comece.
