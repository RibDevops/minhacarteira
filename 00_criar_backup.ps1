# ==============================================================================
# BLOCO 0 - SCRIPT 2: CRIAÇÃO DE BACKUP COMPLETO
# ==============================================================================
# Descrição: Cria backup completo do projeto antes de qualquer modificação
# Autor: Otimizzai
# Data: 2026-09-29
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CRIAÇÃO DE BACKUP COMPLETO" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_NAME = "minhacarteira"
$BASE_DIR = "$PSScriptRoot\$PROJECT_NAME"
$BACKUP_DIR = "$PSScriptRoot\backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_NAME = "backup_${PROJECT_NAME}_${TIMESTAMP}"
$BACKUP_PATH = Join-Path $BACKUP_DIR $BACKUP_NAME

# ==============================================================================
# VALIDAÇÕES INICIAIS
# ==============================================================================

if (-not (Test-Path $BASE_DIR)) {
    Write-Host "✗ Projeto não encontrado em: $BASE_DIR" -ForegroundColor Red
    Write-Host "Execute primeiro o script 00_setup_ambiente.ps1" -ForegroundColor Yellow
    exit 1
}

# Criar diretório de backups se não existir
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -Path $BACKUP_DIR -ItemType Directory | Out-Null
    Write-Host "✓ Diretório de backups criado: $BACKUP_DIR" -ForegroundColor Green
}

# ==============================================================================
# CRIAÇÃO DO BACKUP
# ==============================================================================

Write-Host "Criando backup do projeto..." -ForegroundColor Cyan
Write-Host "Origem: $BASE_DIR" -ForegroundColor White
Write-Host "Destino: $BACKUP_PATH" -ForegroundColor White
Write-Host ""

try {
    # Copiar projeto completo
    Copy-Item -Path $BASE_DIR -Destination $BACKUP_PATH -Recurse -Force
    
    Write-Host "✓ Backup criado com sucesso" -ForegroundColor Green
    
    # Calcular tamanho do backup
    $backupSize = (Get-ChildItem -Path $BACKUP_PATH -Recurse | Measure-Object -Property Length -Sum).Sum
    $backupSizeMB = [math]::Round($backupSize / 1MB, 2)
    
    Write-Host "Tamanho do backup: $backupSizeMB MB" -ForegroundColor White
    
    # Criar arquivo de metadados
    $metadataPath = Join-Path $BACKUP_DIR "${BACKUP_NAME}_metadata.txt"
    
    $metadata = @"
BACKUP MINHACARTEIRA
====================
Data/Hora: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Origem: $BASE_DIR
Destino: $BACKUP_PATH
Tamanho: $backupSizeMB MB
Hash SHA256: Calculando...
"@
    
    $metadata | Out-File -FilePath $metadataPath -Encoding UTF8
    
    Write-Host "✓ Metadados salvos em: $metadataPath" -ForegroundColor Green
    
} catch {
    Write-Host "✗ Erro ao criar backup: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ==============================================================================
# LISTAR BACKUPS EXISTENTES
# ==============================================================================

Write-Host "=== BACKUPS DISPONÍVEIS ===" -ForegroundColor Cyan
Write-Host ""

$backups = Get-ChildItem -Path $BACKUP_DIR -Directory | Sort-Object CreationTime -Descending

if ($backups.Count -eq 0) {
    Write-Host "Nenhum backup anterior encontrado" -ForegroundColor Yellow
} else {
    foreach ($backup in $backups) {
        $size = (Get-ChildItem -Path $backup.FullName -Recurse | Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        
        Write-Host "• $($backup.Name)" -ForegroundColor White
        Write-Host "  Data: $($backup.CreationTime)" -ForegroundColor Gray
        Write-Host "  Tamanho: $sizeMB MB" -ForegroundColor Gray
        Write-Host ""
    }
}

# ==============================================================================
# INSTRUÇÕES DE RESTAURAÇÃO
# ==============================================================================

Write-Host "=== COMO RESTAURAR ESTE BACKUP ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Navegue até: $BACKUP_DIR" -ForegroundColor White
Write-Host "2. Copie a pasta: $BACKUP_NAME" -ForegroundColor White
Write-Host "3. Substitua a pasta atual do projeto" -ForegroundColor White
Write-Host ""
Write-Host "Ou execute:" -ForegroundColor White
Write-Host "Remove-Item -Path '$BASE_DIR' -Recurse -Force" -ForegroundColor Cyan
Write-Host "Copy-Item -Path '$BACKUP_PATH' -Destination '$BASE_DIR' -Recurse" -ForegroundColor Cyan

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  BACKUP CONCLUÍDO" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan