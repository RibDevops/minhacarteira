# ==============================================================================
# ANALISE DO REPOSITORIO ATUAL
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  ANALISE DO REPOSITORIO" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot

# ==============================================================================
# 1) GIT PULL
# ==============================================================================
Write-Host "ETAPA 1: GIT PULL" -ForegroundColor Yellow
Write-Host ""

Push-Location $REPO_DIR

$pullOut = & git pull origin main 2>&1
Write-Host $pullOut
Write-Host ""

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao fazer git pull. Verifique a saida acima." -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "OK: git pull concluido" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# 2) STATUS DO GIT
# ==============================================================================
Write-Host "ETAPA 2: GIT STATUS" -ForegroundColor Yellow
Write-Host ""

$statusOut = & git status
Write-Host $statusOut
Write-Host ""

# ==============================================================================
# 3) LISTA DE ARQUIVOS NO REPOSITORIO
# ==============================================================================
Write-Host "ETAPA 3: ARQUIVOS NO REPOSITORIO" -ForegroundColor Yellow
Write-Host ""

$allFiles = Get-ChildItem -Path $REPO_DIR -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch '\\\.git\\' } |
    Select-Object -ExpandProperty FullName

if ($allFiles.Count -eq 0) {
    Write-Host "ATENCAO: Nenhum arquivo encontrado (exceto .git)" -ForegroundColor Red
    Write-Host ""
    Write-Host "O repositorio parece estar vazio ou conter apenas arquivos Git." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ("Total de arquivos (exceto .git): {0}" -f $allFiles.Count) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Arquivos encontrados:" -ForegroundColor White
    foreach ($f in $allFiles) {
        $rel = $f.Replace($REPO_DIR, "").TrimStart('\')
        Write-Host "  $rel" -ForegroundColor Gray
    }
}

Write-Host ""

# ==============================================================================
# 4) ESTRUTURA DE PASTAS
# ==============================================================================
Write-Host "ETAPA 4: ESTRUTURA DE PASTAS" -ForegroundColor Yellow
Write-Host ""

$folders = Get-ChildItem -Path $REPO_DIR -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\\.git\\' }

if ($folders.Count -eq 0) {
    Write-Host "ATENCAO: Nenhuma pasta encontrada (exceto .git)" -ForegroundColor Red
} else {
    Write-Host ("Total de pastas: {0}" -f $folders.Count) -ForegroundColor Cyan
    Write-Host ""
    foreach ($d in $folders) {
        $rel = $d.FullName.Replace($REPO_DIR, "").TrimStart('\')
        Write-Host "  $rel\" -ForegroundColor Gray
    }
}

Write-Host ""

# ==============================================================================
# 5) CHECAGEM DE ARQUIVOS ESSENCIAIS
# ==============================================================================
Write-Host "ETAPA 5: CHECAGEM DE ARQUIVOS ESSENCIAIS" -ForegroundColor Yellow
Write-Host ""

$essential = @(
    "pom.xml",
    "README.md",
    ".gitignore",
    "src\main\java",
    "src\main\resources",
    "src\test\java"
)

$found = @()
$missing = @()

foreach ($item in $essential) {
    $fullPath = Join-Path $REPO_DIR $item
    if (Test-Path $fullPath) {
        Write-Host "  OK: $item" -ForegroundColor Green
        $found += $item
    } else {
        Write-Host "  FALTA: $item" -ForegroundColor Red
        $missing += $item
    }
}

Write-Host ""

# ==============================================================================
# 6) ULTIMO COMMIT
# ==============================================================================
Write-Host "ETAPA 6: ULTIMO COMMIT" -ForegroundColor Yellow
Write-Host ""

$lastCommit = & git log -1 --oneline
Write-Host "  $lastCommit" -ForegroundColor Cyan

Write-Host ""

# ==============================================================================
# 7) BRANCHES
# ==============================================================================
Write-Host "ETAPA 7: BRANCHES DISPONIVEIS" -ForegroundColor Yellow
Write-Host ""

$branches = & git branch -a
Write-Host $branches

Write-Host ""

# ==============================================================================
# DIAGNOSTICO FINAL
# ==============================================================================
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  DIAGNOSTICO FINAL" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

if ($missing.Count -eq $essential.Count) {
    Write-Host "CONCLUSAO: O repositorio esta VAZIO ou NAO e um projeto Spring Boot." -ForegroundColor Red
    Write-Host ""
    Write-Host "OPCOES:" -ForegroundColor Yellow
    Write-Host "1. Se o projeto esta em outra branch, execute:" -ForegroundColor White
    Write-Host "   git checkout <nome-da-branch>" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Se o repositorio esta realmente vazio, voce precisa:" -ForegroundColor White
    Write-Host "   a) Criar um projeto Spring Boot do zero" -ForegroundColor Gray
    Write-Host "   b) Ou fazer push de um projeto existente" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Se voce quer que EU crie a estrutura Spring Boot completa:" -ForegroundColor White
    Write-Host "   Confirme e eu gero os scripts para criar o projeto base." -ForegroundColor Gray
} elseif ($missing.Count -gt 0) {
    Write-Host "CONCLUSAO: Repositorio PARCIALMENTE configurado." -ForegroundColor Yellow
    Write-Host ""
    Write-Host ("Itens faltando: {0}" -f ($missing -join ", ")) -ForegroundColor Red
} else {
    Write-Host "CONCLUSAO: Repositorio OK. Estrutura Spring Boot detectada." -ForegroundColor Green
}

Pop-Location

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan