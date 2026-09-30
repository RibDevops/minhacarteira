# ==============================================================================
# BLOCO 0 - CORRIGIR .ENV (VERSAO FINAL - LIMPA DUPLICATAS)
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CORRIGIR .ENV - VERSAO FINAL" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
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

# Gerar chaves
Write-Host "Gerando chaves seguras..." -ForegroundColor Yellow

$fernetKey = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
$secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

Write-Host "  FERNET_KEY: $fernetKey" -ForegroundColor Green
Write-Host "  SECRET_KEY: $($secretKey.Substring(0,20))..." -ForegroundColor Green
Write-Host ""

# Criar .env limpo
Write-Host "Criando .env limpo (sem duplicatas)..." -ForegroundColor Yellow

$envContent = @"
# ==============================================================================
# DJANGO SETTINGS
# ==============================================================================
SECRET_KEY=$secretKey
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# ==============================================================================
# CRIPTOGRAFIA (usado em encrypted_model_fields)
# ==============================================================================
FERNET_KEY=$fernetKey

# ==============================================================================
# BANCO DE DADOS
# ==============================================================================
# SQLite (padrao Django)
# DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL (producao)
# DATABASE_URL=postgresql://user:password@localhost:5432/minhacarteira

# ==============================================================================
# CONFIGURACOES REGIONAIS
# ==============================================================================
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo

# ==============================================================================
# EMAIL (opcional - para reset de senha)
# ==============================================================================
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=seu-email@gmail.com
# EMAIL_HOST_PASSWORD=sua-senha-de-app
# EMAIL_USE_TLS=True
# DEFAULT_FROM_EMAIL=noreply@minhacarteira.com

# ==============================================================================
# SEGURANCA (producao)
# ==============================================================================
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True
"@

# Backup do .env antigo (se existir)
if (Test-Path $envFile) {
    $backupFile = "$envFile.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item -Path $envFile -Destination $backupFile
    Write-Host "Backup do .env antigo criado: $backupFile" -ForegroundColor Yellow
}

# Salvar novo .env
$envContent | Out-File -FilePath $envFile -Encoding UTF8
Write-Host ".env criado com sucesso!" -ForegroundColor Green
Write-Host ""

# Testar Django
Write-Host "Testando Django..." -ForegroundColor Yellow
python manage.py check

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO na configuracao. Verifique acima." -ForegroundColor Red
    exit 1
}

Write-Host "Django OK!" -ForegroundColor Green
Write-Host ""

# Migrations
Write-Host "Rodando migrations..." -ForegroundColor Yellow
python manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO nas migrations" -ForegroundColor Red
    exit 1
}

Write-Host "Migrations OK!" -ForegroundColor Green
Write-Host ""

# Collectstatic
Write-Host "Coletando arquivos estaticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear 2>&1 | Out-Null
Write-Host "Arquivos estaticos OK!" -ForegroundColor Green
Write-Host ""

# Superusuario
Write-Host "Verificando superusuario..." -ForegroundColor Yellow
$hasSuperuser = python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" 2>&1

if ($hasSuperuser -match "True") {
    Write-Host "Superusuario ja existe" -ForegroundColor Green
} else {
    Write-Host "Nenhum superusuario encontrado" -ForegroundColor Yellow
    $response = Read-Host "Deseja criar agora? (S/N)"
    
    if ($response -match '^[sS]$') {
        python manage.py createsuperuser
    }
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  AMBIENTE CONFIGURADO COM SUCESSO!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "TESTE AGORA:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Acesse:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "Depois de confirmar funcionamento, execute:" -ForegroundColor Yellow
Write-Host "  .\01_analisar_css.ps1" -ForegroundColor White
Write-Host ""