# ==============================================================================
# BLOCO 4 - REFATORAR CUSTOM.CSS PARA iOS-STYLE
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  REFATORAR CUSTOM.CSS - iOS-STYLE" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
$CSS_DIR = Join-Path $REPO_DIR "static\css"
$CUSTOM_CSS = Join-Path $CSS_DIR "custom.css"
$CUSTOM_NEW = Join-Path $CSS_DIR "custom-ios.css"

# Backup
if (Test-Path $CUSTOM_CSS) {
    $backup = "$CUSTOM_CSS.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item -Path $CUSTOM_CSS -Destination $backup
    Write-Host "Backup criado: $backup" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Criando custom-ios.css (versao refatorada)..." -ForegroundColor Yellow
Write-Host ""

$customIOSContent = @'
/*
==============================================================================
CUSTOM CSS - iOS-STYLE (REFATORADO)
==============================================================================

CSS customizado do MinhaCarteira refatorado para usar design tokens
e seguir padroes visuais do iOS/iPadOS.

Substituicoes principais:
- Cores hardcoded -> variaveis CSS (var(--color-*))
- Espacamentos fixos -> escala padronizada (var(--spacing-*))
- Border-radius inconsistentes -> escala iOS (var(--radius-*))
- Sombras -> sombras suaves iOS (var(--shadow-*))
- Tipografia -> fonte do sistema (var(--font-primary))

Ultima atualizacao: 30/09/2026
==============================================================================
*/

/*
==============================================================================
LAYOUT PRINCIPAL
==============================================================================
*/

body {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-family: var(--font-primary);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.main-container {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: var(--spacing-6) var(--spacing-4);
}

@media (min-width: 768px) {
  .main-container {
    padding: var(--spacing-8) var(--spacing-6);
  }
}

/*
==============================================================================
NAVBAR iOS-STYLE
==============================================================================
*/

.navbar-ios {
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  min-height: var(--navbar-height);
  padding: var(--spacing-3) 0;
}

.navbar-brand-ios {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  transition: color var(--transition-fast);
}

.navbar-brand-ios:hover {
  color: var(--color-primary);
}

.navbar-nav-ios {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-link-ios {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.nav-link-ios:hover {
  color: var(--text-primary);
  background-color: var(--bg-hover);
}

.nav-link-ios.active {
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}

/*
==============================================================================
DASHBOARD
==============================================================================
*/

.dashboard-header {
  margin-bottom: var(--spacing-8);
}

.dashboard-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-2) 0;
}

.dashboard-subtitle {
  font-size: var(--font-size-base);
  color: var(--text-tertiary);
  margin: 0;
}

/* Cards de resumo */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-8);
}

.summary-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.summary-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.summary-card-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 var(--spacing-2) 0;
}

.summary-card-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-1) 0;
}

.summary-card-change {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  margin: 0;
}

.summary-card-change.positive {
  color: var(--color-success);
}

.summary-card-change.negative {
  color: var(--color-danger);
}

/* Cards de receita/despesa com cor */
.summary-card-success {
  border-left: 4px solid var(--color-success);
}

.summary-card-danger {
  border-left: 4px solid var(--color-danger);
}

.summary-card-primary {
  border-left: 4px solid var(--color-primary);
}

/*
==============================================================================
TABELAS iOS-STYLE
==============================================================================
*/

.table-ios-container {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.table-ios {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-base);
}

.table-ios thead {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.table-ios th {
  padding: var(--spacing-4) var(--spacing-5);
  text-align: left;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table-ios td {
  padding: var(--spacing-4) var(--spacing-5);
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.table-ios tbody tr {
  transition: background-color var(--transition-fast);
}

.table-ios tbody tr:hover {
  background-color: var(--bg-hover);
}

.table-ios tbody tr:last-child td {
  border-bottom: none;
}

/* Celulas com badges */
.table-ios .badge-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

/* Acoes da tabela */
.table-actions {
  display: flex;
  gap: var(--spacing-2);
}

.table-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: var(--radius-md);
  border: none;
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.table-action-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  transform: scale(1.05);
}

.table-action-btn.danger:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

/*
==============================================================================
FORMULARIOS
==============================================================================
*/

.form-section {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--spacing-8);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--spacing-6);
}

.form-section-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-6) 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-5);
  margin-bottom: var(--spacing-5);
}

@media (min-width: 768px) {
  .form-row-2 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .form-row-3 {
    grid-template-columns: repeat(3, 1fr);
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
  margin-top: var(--spacing-8);
  padding-top: var(--spacing-6);
  border-top: 1px solid var(--border-color);
}

/*
==============================================================================
MODALS iOS-STYLE
==============================================================================
*/

.modal-ios .modal-content {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
}

.modal-ios .modal-header {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: var(--spacing-6);
}

.modal-ios .modal-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.modal-ios .modal-body {
  padding: var(--spacing-8) var(--spacing-6);
}

.modal-ios .modal-footer {
  background-color: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: var(--spacing-5) var(--spacing-6);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
}

.modal-ios .close {
  background-color: var(--bg-tertiary);
  border: none;
  border-radius: var(--radius-full);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: var(--font-size-xl);
  opacity: 1;
  transition: all var(--transition-fast);
}

.modal-ios .close:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

/*
==============================================================================
EMPTY STATES
==============================================================================
*/

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-16) var(--spacing-8);
  text-align: center;
}

.empty-state-icon {
  font-size: 64px;
  color: var(--text-tertiary);
  margin-bottom: var(--spacing-6);
}

.empty-state-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--spacing-3) 0;
}

.empty-state-message {
  font-size: var(--font-size-base);
  color: var(--text-tertiary);
  max-width: 400px;
  margin: 0 0 var(--spacing-8) 0;
}

/*
==============================================================================
LOADING STATES
==============================================================================
*/

.loading-spinner {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: var(--radius-full);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.loading-content {
  background-color: var(--bg-card);
  border-radius: var(--radius-xl);
  padding: var(--spacing-8);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
}

.loading-content .loading-spinner {
  width: 48px;
  height: 48px;
  border-width: 4px;
}

.loading-text {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
}

/*
==============================================================================
GRAFICOS (CHARTS)
==============================================================================
*/

.chart-container {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--spacing-6);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid var(--border-color);
}

.chart-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.chart-wrapper {
  position: relative;
  height: 300px;
}

@media (min-width: 768px) {
  .chart-wrapper {
    height: 400px;
  }
}

/*
==============================================================================
RESPONSIVIDADE MOBILE
==============================================================================
*/

@media (max-width: 767px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .main-container {
    padding: var(--spacing-4) var(--spacing-3);
  }
  
  .dashboard-title {
    font-size: var(--font-size-2xl);
  }
  
  .form-section {
    padding: var(--spacing-5);
  }
  
  .table-ios-container {
    overflow-x: auto;
  }
  
  .table-ios {
    min-width: 600px;
  }
}

/*
==============================================================================
UTILITARIOS
==============================================================================
*/

/* Espacamentos */
.mt-ios-8 { margin-top: var(--spacing-8); }
.mb-ios-8 { margin-bottom: var(--spacing-8); }
.my-ios-8 { margin-top: var(--spacing-8); margin-bottom: var(--spacing-8); }

.mt-ios-6 { margin-top: var(--spacing-6); }
.mb-ios-6 { margin-bottom: var(--spacing-6); }
.my-ios-6 { margin-top: var(--spacing-6); margin-bottom: var(--spacing-6); }

/* Cores de texto */
.text-ios-success { color: var(--color-success); }
.text-ios-danger { color: var(--color-danger); }
.text-ios-warning { color: var(--color-warning); }
.text-ios-primary { color: var(--color-primary); }
.text-ios-secondary { color: var(--text-secondary); }
.text-ios-tertiary { color: var(--text-tertiary); }

/* Fundo */
.bg-ios-card { background-color: var(--bg-card); }
.bg-ios-secondary { background-color: var(--bg-secondary); }

/* Bordas arredondadas */
.rounded-ios-lg { border-radius: var(--radius-lg); }
.rounded-ios-xl { border-radius: var(--radius-xl); }
.rounded-ios-2xl { border-radius: var(--radius-2xl); }

/* Sombras */
.shadow-ios-sm { box-shadow: var(--shadow-sm); }
.shadow-ios-md { box-shadow: var(--shadow-md); }
.shadow-ios-lg { box-shadow: var(--shadow-lg); }
'@

# Salvar arquivo
$customIOSContent | Out-File -FilePath $CUSTOM_NEW -Encoding UTF8
Write-Host "Arquivo criado: $CUSTOM_NEW" -ForegroundColor Green
Write-Host ""

# Atualizar base.html para usar custom-ios.css
$baseHTML = Join-Path $REPO_DIR "templates\base.html"

if (Test-Path $baseHTML) {
    Write-Host "Atualizando base.html para usar custom-ios.css..." -ForegroundColor Yellow
    
    $baseContent = Get-Content $baseHTML -Raw
    
    # Backup
    $baseBackup = "$baseHTML.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item -Path $baseHTML -Destination $baseBackup
    
    # Substituir custom.css por custom-ios.css
    $baseContent = $baseContent -replace 'custom\.css', 'custom-ios.css'
    
    $baseContent | Out-File -FilePath $baseHTML -Encoding UTF8
    Write-Host "base.html atualizado!" -ForegroundColor Green
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CUSTOM.CSS REFATORADO COM SUCESSO!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Arquivos criados:" -ForegroundColor Yellow
Write-Host "  - static/css/custom-ios.css (versao refatorada)" -ForegroundColor White
Write-Host "  - Backups criados automaticamente" -ForegroundColor White
Write-Host ""
Write-Host "TESTE AGORA:" -ForegroundColor Yellow
Write-Host "  1. python manage.py runserver" -ForegroundColor White
Write-Host "  2. Acesse http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  3. Verifique o novo visual iOS-style" -ForegroundColor White
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "  .\05_integrar_dark_mode.ps1 (integrar dark mode com tokens)" -ForegroundColor White
Write-Host "  .\06_otimizar_responsividade.ps1 (melhorar mobile)" -ForegroundColor White
Write-Host ""