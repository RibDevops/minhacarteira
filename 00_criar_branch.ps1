# ==============================================================================
# BLOCO 0 - SCRIPT 3: CRIAÇÃO DE BRANCH DE REFATORAÇÃO
# ==============================================================================
# Descrição: Cria branch dedicada para refatoração
# Autor: Otimizzai
# Data: 2026-09-29
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CRIAÇÃO DE BRANCH DE REFATORAÇÃO" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_NAME = "minhacarteira"
$BASE_DIR = "$PSScriptRoot\$PROJECT_NAME"
$BRANCH_NAME = "refactor/modernizacao"

# ==============================================================================
# VALIDAÇÕES
# ==============================================================================

if (-not (Test-Path $BASE_DIR)) {
    Write-Host "✗ Projeto não encontrado" -ForegroundColor Red
    exit 1
}

Push-Location $BASE_DIR

# Verificar se é um repositório Git
if (-not (Test-Path ".git")) {
    Write-Host "✗ Não é um repositório Git" -ForegroundColor Red
    Pop-Location
    exit 1
}

# ==============================================================================
# VERIFICAR STATUS DO REPOSITÓRIO
# ==============================================================================

Write-Host "Verificando status do repositório..." -ForegroundColor Cyan
Write-Host ""

$status = git status --porcelain

if ($status) {
    Write-Host "⚠ Existem mudanças não commitadas:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    
    $response = Read-Host "Deseja fazer commit dessas mudanças antes de criar a branch? (S/N)"
    
    if ($response -eq "S" -or $response -eq "s") {
        git add .
        git commit -m "chore: commit antes de iniciar refatoração"
        Write-Host "✓ Mudanças commitadas" -ForegroundColor Green
    }
}

# ==============================================================================
# CRIAR BRANCH
# ==============================================================================

Write-Host ""
Write-Host "Criando branch: $BRANCH_NAME" -ForegroundColor Cyan

# Verificar se branch já existe
$branchExists = git branch --list $BRANCH_NAME

if ($branchExists) {
    Write-Host "⚠ Branch '$BRANCH_NAME' já existe" -ForegroundColor Yellow
    $response = Read-Host "Deseja mudar para ela mesmo assim? (S/N)"
    
    if ($response -eq "S" -or $response -eq "s") {
        git checkout $BRANCH_NAME
        Write-Host "✓ Mudado para branch existente" -ForegroundColor Green
    }
} else {
    git checkout -b $BRANCH_NAME
    Write-Host "✓ Branch criada e ativada" -ForegroundColor Green
}

Write-Host ""
Write-Host "Branch atual: $(git branch --show-current)" -ForegroundColor White

Pop-Location

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  BRANCH CRIADA COM SUCESSO" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PRÓXIMO PASSO:" -ForegroundColor Yellow
Write-Host "Execute: 00_auditoria_completa.ps1" -ForegroundColor White