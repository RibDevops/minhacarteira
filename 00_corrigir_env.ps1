# ==============================================================================
# BLOCO 0 - CORRIGIR CONFIGURACAO DO .ENV
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CORRIGIR CONFIGURACAO .ENV" -ForegroundColor Cyan
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
    Write-Host "ERRO: Ambiente virtual nao encontrado. Execute 00_configurar_ambiente.ps1 primeiro" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Gerar FERNET_KEY
Write-Host "Gerando FERNET_KEY valida..." -ForegroundColor Yellow

$fernetKeyScript = @"
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
"@

$fernetKey = python -c $fernetKeyScript

if ($LASTEXITCODE -ne 0 -or -not $fernetKey) {
    Write-Host "ERRO ao gerar FERNET_KEY" -ForegroundColor Red
    exit 1
}

Write-Host "FERNET_KEY gerada: $fernetKey" -ForegroundColor Green
Write-Host ""

# Gerar SECRET_KEY do Django
Write-Host "Gerando SECRET_KEY do Django..." -ForegroundColor Yellow

$secretKeyScript = @"
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
"@

$secretKey = python -c $secretKeyScript

if ($LASTEXITCODE -ne 0 -or -not $secretKey) {
    Write-Host "ERRO ao gerar SECRET_KEY" -ForegroundColor Red
    exit 1
}

Write-Host "SECRET_KEY gerada: $($secretKey.Substring(0,20))..." -ForegroundColor Green
Write-Host ""

# Criar/atualizar .env
if (Test-Path $envFile) {
    Write-Host "Arquivo .env ja existe. Atualizando chaves..." -ForegroundColor Yellow
    
    $envContent = Get-Content $envFile -Raw
    
    # Atualizar FERNET_KEY
    if ($envContent -match "FERNET_KEY=") {
        $envContent = $envContent -replace "FERNET_KEY=.*", "FERNET_KEY=$fernetKey"
        Write-Host "  FERNET_KEY atualizada" -ForegroundColor Green
    } else {
        $envContent += "`nFERNET_KEY=$fernetKey"
        Write-Host "  FERNET_KEY adicionada" -ForegroundColor Green
    }
    
    # Atualizar SECRET_KEY
    if ($envContent -match "SECRET_KEY=") {
        $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$secretKey"
        Write-Host "  SECRET_KEY atualizada" -ForegroundColor Green
    } else {
        $envContent += "`nSECRET_KEY=$secretKey"
        Write-Host "  SECRET_KEY adicionada" -ForegroundColor Green
    }
    
    # Garantir DEBUG=True
    if ($envContent -match "DEBUG=") {
        $envContent = $envContent -replace "DEBUG=.*", "DEBUG=True"
    } else {
        $envContent += "`nDEBUG=True"
    }
    
    # Salvar
    $envContent | Out-File -FilePath $envFile -Encoding UTF8 -NoNewline
    
} else {
    Write-Host "Criando novo arquivo .env..." -ForegroundColor Yellow
    
    $envTemplate = @"
# Django Settings
SECRET_KEY=$secretKey
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Criptografia (Fernet)
FERNET_KEY=$fernetKey

# Banco de dados (SQLite padrao)
# DATABASE_URL=sqlite:///db.sqlite3

# Configuracoes opcionais
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo
"@
    
    $envTemplate | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "Arquivo .env criado com sucesso!" -ForegroundColor Green
}

Write-Host ""

# Testar configuracao
Write-Host "Testando configuracao do Django..." -ForegroundColor Yellow

$testScript = @"
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
print('OK')
"@

$testResult = python -c $testScript 2>&1

if ($testResult -match "OK") {
    Write-Host "Configuracao OK! Django inicializou corretamente." -ForegroundColor Green
} else {
    Write-Host "ATENCAO: Ainda ha problemas na configuracao:" -ForegroundColor Yellow
    Write-Host $testResult
}

Write-Host ""

# Rodar migrations
Write-Host "Rodando migrations..." -ForegroundColor Yellow
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations aplicadas com sucesso!" -ForegroundColor Green
} else {
    Write-Host "ERRO ao aplicar migrations" -ForegroundColor Red
}

Write-Host ""

# Verificar/criar superusuario
Write-Host "Verificando superusuario..." -ForegroundColor Yellow

$superuserCheck = python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" 2>&1

if ($superuserCheck -match "True") {
    Write-Host "Superusuario ja existe" -ForegroundColor Green
} else {
    Write-Host "Nenhum superusuario encontrado" -ForegroundColor Yellow
    $response = Read-Host "Deseja criar um superusuario agora? (S/N)"
    
    if ($response -match '^[sS]$') {
        Write-Host ""
        Write-Host "Criando superusuario (siga as instrucoes):" -ForegroundColor Yellow
        python manage.py createsuperuser
    }
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACAO CORRIGIDA COM SUCESSO" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para rodar o servidor:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Acesse:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8000/        (aplicacao)" -ForegroundColor White
Write-Host "  http://127.0.0.1:8000/admin/  (painel admin)" -ForegroundColor White
Write-Host ""