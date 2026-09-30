# ==============================================================================
# BLOCO 5 - ATUALIZAR IMPORTS CSS NO BASE.HTML
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  ATUALIZAR IMPORTS CSS NO BASE.HTML" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
$BASE_HTML = Join-Path $REPO_DIR "templates\base.html"

if (-not (Test-Path $BASE_HTML)) {
    Write-Host "ERRO: base.html nao encontrado em templates/" -ForegroundColor Red
    exit 1
}

# Backup
$backup = "$BASE_HTML.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $BASE_HTML -Destination $backup
Write-Host "Backup criado: $backup" -ForegroundColor Yellow
Write-Host ""

# Ler conteudo
$content = Get-Content $BASE_HTML -Raw

Write-Host "Analisando imports atuais..." -ForegroundColor Yellow

# Verificar o que ja existe
$hasDesignTokens = $content -match 'design-tokens\.css'
$hasComponents = $content -match 'components\.css'
$hasCustomIOS = $content -match 'custom-ios\.css'

Write-Host "  design-tokens.css: $(if ($hasDesignTokens) { 'JA IMPORTADO' } else { 'FALTANDO' })" -ForegroundColor $(if ($hasDesignTokens) { 'Green' } else { 'Yellow' })
Write-Host "  components.css: $(if ($hasComponents) { 'JA IMPORTADO' } else { 'FALTANDO' })" -ForegroundColor $(if ($hasComponents) { 'Green' } else { 'Yellow' })
Write-Host "  custom-ios.css: $(if ($hasCustomIOS) { 'JA IMPORTADO' } else { 'FALTANDO' })" -ForegroundColor $(if ($hasCustomIOS) { 'Green' } else { 'Yellow' })
Write-Host ""

# Localizar a tag <head>
if ($content -notmatch '<head>') {
    Write-Host "ERRO: Tag <head> nao encontrada no base.html" -ForegroundColor Red
    exit 1
}

Write-Host "Atualizando imports..." -ForegroundColor Yellow

# Remover imports antigos de custom.css e dark-mode.css (se existirem)
$content = $content -replace '<link[^>]*href="[^"]*custom\.css"[^>]*>\s*', ''
$content = $content -replace '<link[^>]*href="[^"]*dark-mode\.css"[^>]*>\s*', ''

# Preparar novos imports (ordem correta)
$newImports = @'

    <!-- CSS iOS-Style (ordem importa) -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/design-tokens.css' %}">
    <link rel="stylesheet" href="{% static 'css/components.css' %}">
    <link rel="stylesheet" href="{% static 'css/custom-ios.css' %}">
'@

# Inserir antes do fechamento do </head>
$content = $content -replace '(</head>)', "$newImports`n    `$1"

# Salvar
$content | Out-File -FilePath $BASE_HTML -Encoding UTF8
Write-Host "base.html atualizado com sucesso!" -ForegroundColor Green
Write-Host ""

# Verificar se fab.css esta sendo usado
Write-Host "Verificando fab.css..." -ForegroundColor Yellow
if ($content -match 'fab\.css') {
    Write-Host "  fab.css ainda esta sendo importado (ok, manteremos por ora)" -ForegroundColor Yellow
} else {
    Write-Host "  fab.css nao encontrado" -ForegroundColor Gray
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  IMPORTS ATUALIZADOS!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ordem de carregamento CSS:" -ForegroundColor Yellow
Write-Host "  1. design-tokens.css (variaveis)" -ForegroundColor White
Write-Host "  2. components.css (componentes base)" -ForegroundColor White
Write-Host "  3. custom-ios.css (estilos especificos)" -ForegroundColor White
Write-Host ""
Write-Host "Teste agora:" -ForegroundColor Yellow
Write-Host "  1. python manage.py collectstatic --noinput" -ForegroundColor White
Write-Host "  2. python manage.py runserver" -ForegroundColor White
Write-Host "  3. Abra http://127.0.0.1:8000/ e veja as mudancas" -ForegroundColor White
Write-Host ""
Write-Host "Se nao aparecer mudancas, pressione Ctrl+Shift+R no navegador" -ForegroundColor Yellow
Write-Host "(hard refresh para limpar cache)" -ForegroundColor Gray
Write-Host ""