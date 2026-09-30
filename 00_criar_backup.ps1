# ==============================================================================
# BLOCO 0 - SCRIPT 1: BACKUP COMPLETO DO PROJETO
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  BACKUP COMPLETO - MINHACARTEIRA" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_DIR = Join-Path $REPO_DIR "backups"
$BACKUP_NAME = "backup_$TIMESTAMP"
$BACKUP_PATH = Join-Path $BACKUP_DIR $BACKUP_NAME

# Criar diretorio de backups
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
    Write-Host "Diretorio de backups criado: $BACKUP_DIR" -ForegroundColor Green
}

Write-Host "Criando backup em: $BACKUP_PATH" -ForegroundColor Yellow
Write-Host ""

# Criar estrutura do backup
New-Item -ItemType Directory -Path $BACKUP_PATH -Force | Out-Null

# Lista de diretorios/arquivos importantes para backup
$itemsToBackup = @(
    "cal",
    "core",
    "templates",
    "static",
    "encrypted_model_fields",
    "manage.py",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "README.md"
)

$totalItems = $itemsToBackup.Count
$current = 0

foreach ($item in $itemsToBackup) {
    $current++
    $sourcePath = Join-Path $REPO_DIR $item
    
    if (Test-Path $sourcePath) {
        Write-Host "[$current/$totalItems] Copiando: $item" -ForegroundColor White
        
        if (Test-Path $sourcePath -PathType Container) {
            # É um diretório
            Copy-Item -Path $sourcePath -Destination $BACKUP_PATH -Recurse -Force
        } else {
            # É um arquivo
            Copy-Item -Path $sourcePath -Destination $BACKUP_PATH -Force
        }
        
        Write-Host "  OK" -ForegroundColor Green
    } else {
        Write-Host "[$current/$totalItems] AVISO: $item nao encontrado, pulando" -ForegroundColor Yellow
    }
}

Write-Host ""

# Criar arquivo de informacoes do backup
$backupInfo = @"
BACKUP CRIADO EM: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
PROJETO: MinhaCarteira (Django)
BRANCH ATUAL: $(git branch --show-current 2>&1)
ULTIMO COMMIT: $(git log -1 --oneline 2>&1)

CONTEUDO DO BACKUP:
$(($itemsToBackup | ForEach-Object { "  - $_" }) -join "`n")

PROPOSITO: Backup antes da refatoracao CSS iOS-style
"@

$backupInfo | Out-File -FilePath (Join-Path $BACKUP_PATH "BACKUP_INFO.txt") -Encoding UTF8

# Verificar tamanho do backup
$backupSize = (Get-ChildItem -Path $BACKUP_PATH -Recurse | Measure-Object -Property Length -Sum).Sum
$backupSizeMB = [math]::Round($backupSize / 1MB, 2)

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  BACKUP CONCLUIDO COM SUCESSO" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Local: $BACKUP_PATH" -ForegroundColor White
Write-Host "Tamanho: $backupSizeMB MB" -ForegroundColor White
Write-Host ""
Write-Host "Para restaurar este backup:" -ForegroundColor Yellow
Write-Host "  Copy-Item -Path '$BACKUP_PATH\*' -Destination '$REPO_DIR' -Recurse -Force" -ForegroundColor Gray
Write-Host ""