# Coordenação entre IAs — Minha Carteira Digital

> Este projeto é trabalhado por mais de uma IA (Claude, Replit Agent, Manus)
> no mesmo repositório. Este arquivo existe porque isso já causou perda de
> trabalho antes (histórico do Git foi substituído por completo numa sessão
> anterior). Regras simples pra não repetir.

## Regras

1. **Antes de começar qualquer tarefa: `git pull`.** Nunca trabalhar sem
   sincronizar primeiro.
2. **Fonte de verdade única por assunto** (evita duas implementações do
   mesmo recurso):
   - API REST → `cal/api/` (serializers, views, urls) — **não criar API em
     outro lugar**.
   - Lógica de negócio → `cal/services.py`
   - Views web → `cal/views/`
   - Nenhuma IA cria pasta própria (tipo `manus/`, `claude/`) com cópias de
     arquivos do projeto pra "trabalhar isolado". Isso gera duplicação e
     confunde quem for ler o código depois. Trabalhar direto nos arquivos
     reais, em uma branch se precisar de isolamento.
3. **Progresso registrado em `MIGRACAO_FLUTTER.md`** (migração Flutter) e
   `ALTERACOES_PENDENTES.md` / `MELHORIAS_DETALHADAS.md` (demais correções).
   Antes de iniciar uma etapa, checar se ela já está marcada como feita por
   outra IA. Depois de concluir, marcar e commitar.
4. **Rodar `python manage.py test cal` antes de cada commit.** Isso já
   pegaria o caso da correção do dashboard que reabriu uma XSS sem ser
   percebida antes do push.
5. **Commits pequenos e descritivos**, um assunto por commit. Evitar
   mensagens genéricas tipo `'refa'`, `'refa23'`, `'modal'` — dificulta saber
   o que mudou sem abrir o diff inteiro.
6. **Arquivos de patch (`.patch`) e scripts de uso único não ficam no
   repositório depois de aplicados.** Aplicar, confirmar que funcionou,
   remover.

## Estado atual (01/08/2026)

- API REST em `cal/api/`: base (Claude) + Recorrências e Dashboard agregado
  (Manus) — íntegro, testado, 22 testes web + endpoints novos passando.
- Pendente: limpar `manus/` (cópias redundantes de `models.py`/`services.py`/
  `serializers.py`/`views.py`, idênticas ou já superadas pelas de `cal/api/`)
  e os `.patch`/`.ps1` soltos ali dentro.
- Próxima etapa da migração Flutter: criar o projeto Flutter em si (etapa 6
  do `MIGRACAO_FLUTTER.md`).

## Se outra IA (ou você) for continuar

Enviar junto, no início da conversa: este arquivo + `MIGRACAO_FLUTTER.md`.
Isso já dá o estado atual sem precisar reexplicar.
