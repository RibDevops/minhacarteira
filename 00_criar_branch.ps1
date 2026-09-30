# ==============================================================================
# BLOCO 0 - SCRIPT 2: CRIAR BRANCH DE REFATORACAO
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CRIAR BRANCH DE REFATORACAO" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
Push-Location $REPO_DIR

# Verificar se estamos em um repositorio Git
if (-not (Test-Path ".git")) {
    Write-Host "ERRO: Diretorio atual nao e um repositorio Git" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Verificar branch atual
$currentBranch = git branch --show-current 2>&1
Write-Host "Branch atual: $currentBranch" -ForegroundColor White
Write-Host ""

# Nome da nova branch
$newBranch = "refactor/ios-modernization"

# Verificar se a branch ja existe
$branchExists = git branch --list $newBranch 2>&1

if ($branchExists) {
    Write-Host "ATENCAO: Branch '$newBranch' ja existe." -ForegroundColor Yellow
    $response = Read-Host "Deseja fazer checkout nela? (S/N)"
    
    if ($response -match '^[sS]$') {
        git checkout $newBranch
        Write-Host "Checkout realizado em '$newBranch'" -ForegroundColor Green
    } else {
        Write-Host "Operacao cancelada." -ForegroundColor Yellow
        Pop-Location
        exit 0
    }
} else {
    Write-Host "Criando nova branch: $newBranch" -ForegroundColor Yellow
    git checkout -b $newBranch
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO ao criar branch" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    Write-Host "Branch criada com sucesso!" -ForegroundColor Green
}

Write-Host ""

# Verificar status
Write-Host "Verificando status do repositorio..." -ForegroundColor Yellow
$status = git status --short 2>&1

if ($status) {
    Write-Host "Arquivos nao commitados detectados:" -ForegroundColor Yellow
    Write-Host $status
    Write-Host ""
    
    $commitResponse = Read-Host "Deseja commitar alteracoes atuais? (S/N)"
    
    if ($commitResponse -match '^[sS]$') {
        Write-Host ""
        Write-Host "Adicionando arquivos..." -ForegroundColor Yellow
        git add .
        
        $commitMsg = @"
chore: preparacao para refatoracao iOS-style

- Backup criado
- Branch de refatoracao iniciada
- Estado atual preservado antes das mudancas

Proximos passos:
- Refatoracao completa do CSS
- Design system iOS (tokens, componentes)
- Modernizacao visual (bordas, sombras, tipografia)
- Responsividade mobile-first
"@
        
        git commit -m $commitMsg
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Commit realizado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "ERRO ao realizar commit" -ForegroundColor Red
            Pop-Location
            exit 1
        }
    }
} else {
    Write-Host "Repositorio limpo (nenhuma alteracao pendente)" -ForegroundColor Green
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  BRANCH CONFIGURADA" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Branch atual: $(git branch --show-current)" -ForegroundColor White
Write-Host ""
Write-Host "Para fazer push da branch:" -ForegroundColor Yellow
Write-Host "  git push -u origin $newBranch" -ForegroundColor Gray
Write-Host ""

Pop-Location