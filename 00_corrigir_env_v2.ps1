# ==============================================================================
# BLOCO 0 - CORRIGIR CONFIGURACAO DO .ENV (V2 - REMOVE DUPLICATAS)
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

# Processar .env linha por linha (remove duplicatas)
if (Test-Path $envFile) {
    Write-Host "Processando arquivo .env existente..." -ForegroundColor Yellow
    
    $existingLines = Get-Content $envFile
    $newLines = @()
    $foundFernet = $false
    $foundSecret = $false
    
    foreach ($line in $existingLines) {
        # Pular linhas antigas de FERNET_KEY e SECRET_KEY
        if ($line -match "^\s*FERNET_KEY=") {
            if (-not $foundFernet) {
                $newLines += "FERNET_KEY=$fernetKey"
                $foundFernet = $true
                Write-Host "  FERNET_KEY substituida" -ForegroundColor Green
            }
            continue
        }
        
        if ($line -match "^\s*SECRET_KEY=") {
            if (-not $foundSecret) {
                $newLines += "SECRET_KEY=$secretKey"
                $foundSecret = $true
                Write-Host "  SECRET_KEY substituida" -ForegroundColor Green
            }
            continue
        }
        
        # Manter outras linhas
        $newLines += $line
    }
    
    # Adicionar chaves se nao existiam
    if (-not $foundFernet) {
        $newLines += "FERNET_KEY=$fernetKey"
        Write-Host "  FERNET_KEY adicionada" -ForegroundColor Green
    }
    
    if (-not $foundSecret) {
        $newLines += "SECRET_KEY=$secretKey"
        Write-Host "  SECRET_KEY adicionada" -ForegroundColor Green
    }
    
    # Garantir DEBUG=True
    $hasDebug = $false
    for ($i = 0; $i -lt $newLines.Count; $i++) {
        if ($newLines[$i] -match "^\s*DEBUG=") {
            $newLines[$i] = "DEBUG=True"
            $hasDebug = $true
            break
        }
    }
    
    if (-not $hasDebug) {
        $newLines += "DEBUG=True"
    }
    
    # Salvar arquivo
    $newLines | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "Arquivo .env atualizado!" -ForegroundColor Green
    
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

# Exibir conteudo do .env (sem valores sensiveis)
Write-Host "Conteudo do .env (resumo):" -ForegroundColor Yellow
$envLines = Get-Content $envFile
foreach ($line in $envLines) {
    if ($line -match "^(FERNET_KEY|SECRET_KEY)=") {
        $key = $line.Split('=')[0]
        Write-Host "  $key=***" -ForegroundColor Gray
    } elseif ($line.Trim() -and -not $line.StartsWith('#')) {
        Write-Host "  $line" -ForegroundColor Gray
    }
}

Write-Host ""

# Testar configuracao
Write-Host "Testando configuracao do Django..." -ForegroundColor Yellow

python manage.py check 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Configuracao OK! Django inicializou corretamente." -ForegroundColor Green
} else {
    Write-Host "ATENCAO: Verificando erros..." -ForegroundColor Yellow
    python manage.py check
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

# Coletar arquivos estaticos
Write-Host "Coletando arquivos estaticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Arquivos estaticos coletados!" -ForegroundColor Green
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
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Rodar servidor de desenvolvimento:" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Acessar aplicacao:" -ForegroundColor White
Write-Host "   http://127.0.0.1:8000/        (home)" -ForegroundColor Gray
Write-Host "   http://127.0.0.1:8000/admin/  (painel admin)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Apos confirmar funcionamento, execute:" -ForegroundColor White
Write-Host "   .\01_analisar_css.ps1  (proximo bloco - refatoracao CSS iOS)" -ForegroundColor Gray
Write-Host ""