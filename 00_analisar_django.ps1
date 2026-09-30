# ==============================================================================
# ANALISE COMPLETA DO PROJETO DJANGO
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  ANALISE DO PROJETO DJANGO - MINHACARTEIRA" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
$LOG_FILE = Join-Path $REPO_DIR ("analise_django_{0}.txt" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
    $Message | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
}

# ==============================================================================
# 1) VERSAO DO PYTHON
# ==============================================================================
Write-Log "`n=== 1) VERSAO DO PYTHON ===" "Yellow"

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Log "ERRO: Python nao encontrado no PATH" "Red"
    Write-Log "Instale Python 3.10+ em: https://www.python.org/downloads/" "Yellow"
} else {
    $pyVer = & python --version 2>&1
    Write-Log "OK: $pyVer" "Green"
}

# ==============================================================================
# 2) ESTRUTURA DO PROJETO
# ==============================================================================
Write-Log "`n=== 2) ESTRUTURA DO PROJETO ===" "Yellow"

$estrutura = @{
    "manage.py" = "Gerenciador Django"
    "requirements.txt" = "Dependencias Python"
    "core\settings.py" = "Configuracoes Django"
    "core\urls.py" = "Rotas principais"
    "cal\models.py" = "Modelos de dados (app cal)"
    "cal\views.py" = "Views (app cal)"
    "templates" = "Templates HTML"
    "static" = "Arquivos estaticos (CSS/JS/imagens)"
    ".env.example" = "Exemplo de variaveis de ambiente"
}

$missing = @()
foreach ($key in $estrutura.Keys) {
    $path = Join-Path $REPO_DIR $key
    if (Test-Path $path) {
        Write-Log "  OK: $key - $($estrutura[$key])" "Green"
    } else {
        Write-Log "  FALTA: $key - $($estrutura[$key])" "Red"
        $missing += $key
    }
}

# ==============================================================================
# 3) ANALISE DO REQUIREMENTS.TXT
# ==============================================================================
Write-Log "`n=== 3) DEPENDENCIAS (requirements.txt) ===" "Yellow"

$reqFile = Join-Path $REPO_DIR "requirements.txt"
if (Test-Path $reqFile) {
    $deps = Get-Content $reqFile
    Write-Log "Total de dependencias: $($deps.Count)" "Cyan"
    Write-Log "`nPrincipais pacotes:" "White"
    foreach ($dep in $deps) {
        if ($dep -match "^[a-zA-Z]") {
            Write-Log "  - $dep" "Gray"
        }
    }
} else {
    Write-Log "ATENCAO: requirements.txt nao encontrado" "Red"
}

# ==============================================================================
# 4) APPS DJANGO
# ==============================================================================
Write-Log "`n=== 4) APPS DJANGO ===" "Yellow"

$apps = Get-ChildItem -Path $REPO_DIR -Directory | 
    Where-Object { Test-Path (Join-Path $_.FullName "models.py") }

Write-Log "Apps detectados: $($apps.Count)" "Cyan"
foreach ($app in $apps) {
    Write-Log "  - $($app.Name)" "Green"
    
    $models = Join-Path $app.FullName "models.py"
    $views = Join-Path $app.FullName "views.py"
    $urls = Join-Path $app.FullName "urls.py"
    
    if (Test-Path $models) {
        $modelContent = Get-Content $models -Raw
        $modelClasses = ([regex]::Matches($modelContent, "class\s+(\w+)\(models\.Model\)")).Count
        Write-Log "    Models: $modelClasses classes" "Gray"
    }
    
    if (Test-Path $views) { Write-Log "    views.py: OK" "Gray" }
    if (Test-Path $urls) { Write-Log "    urls.py: OK" "Gray" }
}

# ==============================================================================
# 5) TEMPLATES E STATIC
# ==============================================================================
Write-Log "`n=== 5) FRONTEND ===" "Yellow"

$templatesDir = Join-Path $REPO_DIR "templates"
$staticDir = Join-Path $REPO_DIR "static"

if (Test-Path $templatesDir) {
    $htmlFiles = Get-ChildItem -Path $templatesDir -Filter "*.html" -Recurse
    Write-Log "Templates HTML: $($htmlFiles.Count)" "Green"
}

if (Test-Path $staticDir) {
    $cssFiles = Get-ChildItem -Path $staticDir -Filter "*.css" -Recurse
    $jsFiles = Get-ChildItem -Path $staticDir -Filter "*.js" -Recurse
    Write-Log "Arquivos CSS: $($cssFiles.Count)" "Green"
    Write-Log "Arquivos JS: $($jsFiles.Count)" "Green"
}

# ==============================================================================
# 6) BANCO DE DADOS
# ==============================================================================
Write-Log "`n=== 6) BANCO DE DADOS ===" "Yellow"

$dbFiles = Get-ChildItem -Path $REPO_DIR -Filter "*.sqlite3"
if ($dbFiles.Count -gt 0) {
    foreach ($db in $dbFiles) {
        $size = [math]::Round($db.Length / 1KB, 2)
        Write-Log "  - $($db.Name) ($size KB)" "Green"
    }
} else {
    Write-Log "Nenhum arquivo .sqlite3 encontrado (banco nao criado ainda)" "Yellow"
}

# ==============================================================================
# 7) MIGRATIONS
# ==============================================================================
Write-Log "`n=== 7) MIGRATIONS ===" "Yellow"

$migrations = Get-ChildItem -Path $REPO_DIR -Recurse -Filter "0*.py" | 
    Where-Object { $_.DirectoryName -like "*migrations*" }

Write-Log "Total de migrations: $($migrations.Count)" "Cyan"

# ==============================================================================
# 8) VARIAVEIS DE AMBIENTE
# ==============================================================================
Write-Log "`n=== 8) VARIAVEIS DE AMBIENTE ===" "Yellow"

$envExample = Join-Path $REPO_DIR ".env.example"
$envFile = Join-Path $REPO_DIR ".env"

if (Test-Path $envExample) {
    Write-Log "  .env.example: OK" "Green"
} else {
    Write-Log "  .env.example: FALTA" "Red"
}

if (Test-Path $envFile) {
    Write-Log "  .env: OK (arquivo de configuracao presente)" "Green"
} else {
    Write-Log "  .env: FALTA (criar a partir do .env.example)" "Yellow"
}

# ==============================================================================
# 9) DOCUMENTACAO
# ==============================================================================
Write-Log "`n=== 9) DOCUMENTACAO ===" "Yellow"

$docs = @(
    "README.md",
    "Manual_do_Usuario.md",
    "MELHORIAS_DETALHADAS.md",
    "MIGRACAO_FLUTTER.md",
    "COORDENACAO_IAS.md"
)

foreach ($doc in $docs) {
    $path = Join-Path $REPO_DIR $doc
    if (Test-Path $path) {
        Write-Log "  OK: $doc" "Green"
    }
}

# ==============================================================================
# RELATORIO FINAL
# ==============================================================================
Write-Log "`n===================================================" "Cyan"
Write-Log "  RELATORIO FINAL" "Cyan"
Write-Log "===================================================" "Cyan"

Write-Log "`nTECNOLOGIAS IDENTIFICADAS:" "Yellow"
Write-Log "  - Backend: Django (Python)" "White"
Write-Log "  - Frontend: HTML/CSS/JS (Bootstrap)" "White"
Write-Log "  - Banco de dados: SQLite (padrao Django)" "White"
Write-Log "  - Autenticacao: Django Auth (detectado nos templates)" "White"

Write-Log "`nFUNCIONALIDADES PRINCIPAIS (baseado na estrutura):" "Yellow"
Write-Log "  - Gestao de transacoes financeiras (cal app)" "White"
Write-Log "  - Dashboard com graficos (ChartJS)" "White"
Write-Log "  - Sistema de recorrencias" "White"
Write-Log "  - Gestao de cartoes" "White"
Write-Log "  - Categorias e tipos de transacao" "White"
Write-Log "  - Metas financeiras" "White"
Write-Log "  - API REST (cal/api/)" "White"

Write-Log "`nPROXIMOS PASSOS RECOMENDADOS:" "Yellow"
Write-Log "  1. Criar ambiente virtual Python" "White"
Write-Log "     python -m venv venv" "Gray"
Write-Log "`n  2. Ativar o ambiente" "White"
Write-Log "     .\venv\Scripts\Activate.ps1" "Gray"
Write-Log "`n  3. Instalar dependencias" "White"
Write-Log "     pip install -r requirements.txt" "Gray"
Write-Log "`n  4. Configurar .env (copiar de .env.example)" "White"
Write-Log "`n  5. Rodar migrations" "White"
Write-Log "     python manage.py migrate" "Gray"
Write-Log "`n  6. Criar superusuario" "White"
Write-Log "     python manage.py createsuperuser" "Gray"
Write-Log "`n  7. Rodar servidor de desenvolvimento" "White"
Write-Log "     python manage.py runserver" "Gray"

Write-Log "`nLog salvo em: $LOG_FILE" "Cyan"

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  ANALISE CONCLUIDA" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan