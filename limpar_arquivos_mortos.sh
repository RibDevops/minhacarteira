#!/usr/bin/env bash
# Remove arquivos desnecessários do projeto. Rodar na raiz (onde fica manage.py).
# Não commita automaticamente — revise com `git status`/`git diff` antes.
set -e

cd "$(dirname "$0")"

echo "== 1. CSS morto (nunca carregado, ou carregado mas sem nenhuma classe usada) =="
git rm -f static/css/all.css static/css/calendar.css \
          static/css/fontawesome.min.css static/css/simple-sidebar.css 2>/dev/null || \
  rm -f static/css/all.css static/css/calendar.css \
        static/css/fontawesome.min.css static/css/simple-sidebar.css

echo "== 2. Removendo os <link> órfãos em templates/base.html =="
sed -i.bak "/css\/simple-sidebar.css/d" templates/base.html
sed -i.bak "/css\/fontawesome.min.css/d" templates/base.html
rm -f templates/base.html.bak

echo "== 3. Parando de versionar staticfiles/ (é output de collectstatic, não código-fonte) =="
if git ls-files staticfiles/ --error-unmatch >/dev/null 2>&1; then
    git rm -r --cached staticfiles/ >/dev/null
fi
if ! grep -qx "staticfiles/" .gitignore 2>/dev/null; then
    echo "staticfiles/" >> .gitignore
fi

echo ""
echo "== Concluído. Revise antes de commitar: =="
git status --short
