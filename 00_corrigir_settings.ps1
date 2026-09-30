# ==============================================================================
# BLOCO 0 - CORRIGIR SETTINGS.PY E .ENV
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CORRIGIR SETTINGS.PY E .ENV" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
$settingsFile = Join-Path $REPO_DIR "core\settings.py"
$envFile = Join-Path $REPO_DIR ".env"

# Ativar ambiente virtual
$venvPath = Join-Path $REPO_DIR "venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "Ambiente virtual ativado" -ForegroundColor Green
} else {
    Write-Host "ERRO: Ambiente virtual nao encontrado" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Analisar settings.py
Write-Host "Analisando core/settings.py..." -ForegroundColor Yellow

if (-not (Test-Path $settingsFile)) {
    Write-Host "ERRO: settings.py nao encontrado" -ForegroundColor Red
    exit 1
}

$settingsContent = Get-Content $settingsFile -Raw

# Identificar variaveis de criptografia necessarias
$needsFernet = $settingsContent -match "FERNET"
$needsFieldEncryption = $settingsContent -match "FIELD_ENCRYPTION_KEY"

Write-Host "  Usa FERNET: $needsFernet" -ForegroundColor Gray
Write-Host "  Usa FIELD_ENCRYPTION_KEY: $needsFieldEncryption" -ForegroundColor Gray
Write-Host ""

# Gerar chaves
Write-Host "Gerando chaves..." -ForegroundColor Yellow

$fernetKey = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
$secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

Write-Host "  FERNET_KEY gerada: $fernetKey" -ForegroundColor Green
Write-Host "  SECRET_KEY gerada: $($secretKey.Substring(0,20))..." -ForegroundColor Green
Write-Host ""

# Criar .env completo
Write-Host "Criando .env com TODAS as variaveis necessarias..." -ForegroundColor Yellow

$envContent = @"
# ==============================================================================
# DJANGO CORE
# ==============================================================================
SECRET_KEY=$secretKey
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# ==============================================================================
# CRIPTOGRAFIA
# Ambas as variaveis usam a mesma chave (compatibilidade)
# ==============================================================================
FERNET_KEY=$fernetKey
FIELD_ENCRYPTION_KEY=$fernetKey

# ==============================================================================
# BANCO DE DADOS
# ==============================================================================
# SQLite (padrao)
# DATABASE_URL=sqlite:///db.sqlite3

# ==============================================================================
# CONFIGURACOES REGIONAIS
# ==============================================================================
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo

# ==============================================================================
# EMAIL (opcional)
# ==============================================================================
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=
# EMAIL_HOST_PASSWORD=
# EMAIL_USE_TLS=True
# DEFAULT_FROM_EMAIL=noreply@minhacarteira.com
"@

# Backup do .env antigo
if (Test-Path $envFile) {
    $backupFile = "$envFile.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item -Path $envFile -Destination $backupFile
    Write-Host "Backup criado: $backupFile" -ForegroundColor Gray
}

# Salvar .env
$envContent | Out-File -FilePath $envFile -Encoding UTF8
Write-Host ".env criado com sucesso!" -ForegroundColor Green
Write-Host ""

# Exibir conteudo (sem valores sensiveis)
Write-Host "Variaveis configuradas:" -ForegroundColor Yellow
Write-Host "  SECRET_KEY=***" -ForegroundColor Gray
Write-Host "  FERNET_KEY=***" -ForegroundColor Gray
Write-Host "  FIELD_ENCRYPTION_KEY=*** (mesma chave do FERNET_KEY)" -ForegroundColor Gray
Write-Host "  DEBUG=True" -ForegroundColor Gray
Write-Host "  ALLOWED_HOSTS=127.0.0.1,localhost" -ForegroundColor Gray
Write-Host ""

# Testar Django
Write-Host "Testando Django..." -ForegroundColor Yellow
$checkOutput = python manage.py check 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Django OK!" -ForegroundColor Green
} else {
    Write-Host "ERRO na configuracao:" -ForegroundColor Red
    Write-Host $checkOutput
    exit 1
}

Write-Host ""

# Migrations
Write-Host "Rodando migrations..." -ForegroundColor Yellow
python manage.py migrate 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations OK!" -ForegroundColor Green
} else {
    Write-Host "ERRO nas migrations. Execute manualmente:" -ForegroundColor Red
    Write-Host "  python manage.py migrate" -ForegroundColor Gray
}

Write-Host ""

# Collectstatic
Write-Host "Coletando arquivos estaticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Arquivos estaticos OK!" -ForegroundColor Green
}

Write-Host ""

# Superusuario
Write-Host "Verificando superusuario..." -ForegroundColor Yellow
$checkSuperuser = python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" 2>&1

if ($checkSuperuser -match "True") {
    Write-Host "Superusuario ja existe" -ForegroundColor Green
} else {
    Write-Host "Nenhum superusuario encontrado" -ForegroundColor Yellow
    $response = Read-Host "Criar superusuario agora? (S/N)"
    
    if ($response -match '^[sS]$') {
        Write-Host ""
        python manage.py createsuperuser
    }
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "TESTE O SERVIDOR:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Acesse:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  http://127.0.0.1:8000/admin/ (se criou superusuario)" -ForegroundColor White
Write-Host ""
Write-Host "Se tudo funcionar, prossiga para a refatoracao CSS:" -ForegroundColor Yellow
Write-Host "  .\01_analisar_css.ps1" -ForegroundColor White
Write-Host ""