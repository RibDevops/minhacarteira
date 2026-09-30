# ==============================================================================
# BLOCO 0 - SCRIPT 3: CONFIGURAR AMBIENTE PYTHON
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURAR AMBIENTE PYTHON - DJANGO" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
Push-Location $REPO_DIR

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    Write-Host "ERRO: Python nao encontrado no PATH" -ForegroundColor Red
    Write-Host "Instale Python 3.10+ em: https://www.python.org/downloads/" -ForegroundColor Yellow
    Pop-Location
    exit 1
}

$pyVersion = python --version 2>&1
Write-Host "OK: $pyVersion" -ForegroundColor Green
Write-Host ""

# Verificar/criar ambiente virtual
$venvPath = Join-Path $REPO_DIR "venv"

if (Test-Path $venvPath) {
    Write-Host "Ambiente virtual ja existe em: $venvPath" -ForegroundColor Yellow
    $response = Read-Host "Deseja recriar? (S/N)"
    
    if ($response -match '^[sS]$') {
        Write-Host "Removendo ambiente virtual antigo..." -ForegroundColor Yellow
        Remove-Item -Path $venvPath -Recurse -Force
        Write-Host "Criando novo ambiente virtual..." -ForegroundColor Yellow
        python -m venv venv
    } else {
        Write-Host "Mantendo ambiente virtual existente." -ForegroundColor Green
    }
} else {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO ao criar ambiente virtual" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Write-Host "Ambiente virtual criado!" -ForegroundColor Green
}

Write-Host ""

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "Ambiente virtual ativado!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Script de ativacao nao encontrado" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""

# Atualizar pip
Write-Host "Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

Write-Host ""

# Instalar dependencias
Write-Host "Instalando dependencias do requirements.txt..." -ForegroundColor Yellow
Write-Host "(Isso pode demorar alguns minutos na primeira vez)" -ForegroundColor Gray
Write-Host ""

pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao instalar dependencias" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "Dependencias instaladas com sucesso!" -ForegroundColor Green
Write-Host ""

# Verificar .env
$envFile = Join-Path $REPO_DIR ".env"
$envExample = Join-Path $REPO_DIR ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Write-Host "Criando .env a partir de .env.example..." -ForegroundColor Yellow
        Copy-Item -Path $envExample -Destination $envFile
        Write-Host "Arquivo .env criado!" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANTE: Edite o arquivo .env e configure:" -ForegroundColor Yellow
        Write-Host "  - SECRET_KEY (gere uma nova chave segura)" -ForegroundColor White
        Write-Host "  - DEBUG=True (para desenvolvimento)" -ForegroundColor White
        Write-Host "  - Outras variaveis conforme necessario" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "ATENCAO: Nem .env nem .env.example encontrados" -ForegroundColor Yellow
        Write-Host "Voce precisara criar o arquivo .env manualmente" -ForegroundColor White
    }
} else {
    Write-Host ".env ja existe, mantendo configuracao atual" -ForegroundColor Green
}

Write-Host ""

# Rodar migrations
Write-Host "Rodando migrations do Django..." -ForegroundColor Yellow
python manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao rodar migrations" -ForegroundColor Red
} else {
    Write-Host "Migrations aplicadas com sucesso!" -ForegroundColor Green
}

Write-Host ""

# Verificar se existe superusuario
Write-Host "Verificando superusuario..." -ForegroundColor Yellow
$superuserCheck = python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" 2>&1

if ($superuserCheck -match "True") {
    Write-Host "Superusuario ja existe" -ForegroundColor Green
} else {
    Write-Host "Nenhum superusuario encontrado" -ForegroundColor Yellow
    $createSuper = Read-Host "Deseja criar um superusuario agora? (S/N)"
    
    if ($createSuper -match '^[sS]$') {
        Write-Host ""
        python manage.py createsuperuser
    }
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  AMBIENTE CONFIGURADO COM SUCESSO" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para rodar o servidor de desenvolvimento:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Para acessar o admin:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "Para rodar testes:" -ForegroundColor Yellow
Write-Host "  python manage.py test" -ForegroundColor White
Write-Host ""

Pop-Location