# ==============================================================================
# BLOCO 3 - CRIAR COMPONENTES BASE iOS-STYLE
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CRIAR COMPONENTES BASE iOS-STYLE" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
$CSS_DIR = Join-Path $REPO_DIR "static\css"
$COMPONENTS_FILE = Join-Path $CSS_DIR "components.css"

# Backup
if (Test-Path $COMPONENTS_FILE) {
    $backup = "$COMPONENTS_FILE.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item -Path $COMPONENTS_FILE -Destination $backup
    Write-Host "Backup criado: $backup" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Criando components.css..." -ForegroundColor Yellow
Write-Host ""

$componentsContent = @'
/*
==============================================================================
COMPONENTES BASE - iOS-STYLE
==============================================================================

Componentes reutilizaveis com design inspirado no iOS/iPadOS.
Usa as variaveis definidas em design-tokens.css.

Componentes incluidos:
- Botoes (.btn-*)
- Cards (.card-ios)
- Inputs (.input-ios, .form-ios)
- Badges (.badge-ios)
- Alerts (.alert-ios)
- Modals (aprimoramentos)

Ultima atualizacao: 30/09/2026
==============================================================================
*/

/*
==============================================================================
BOTOES iOS-STYLE
==============================================================================
*/

.btn-ios {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  min-height: var(--button-height);
  padding: var(--spacing-3) var(--spacing-6);
  font-family: var(--font-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  border: none;
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  text-decoration: none;
  outline: none;
}

.btn-ios:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Botao primario */
.btn-ios-primary {
  background-color: var(--color-primary);
  color: var(--text-inverse);
  box-shadow: var(--shadow-sm);
}

.btn-ios-primary:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.btn-ios-primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: var(--shadow-xs);
}

/* Botao secundario */
.btn-ios-secondary {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
  box-shadow: var(--shadow-xs);
}

.btn-ios-secondary:hover:not(:disabled) {
  background-color: var(--bg-hover);
  box-shadow: var(--shadow-sm);
}

/* Botao success */
.btn-ios-success {
  background-color: var(--color-success);
  color: var(--text-inverse);
  box-shadow: var(--shadow-sm);
}

.btn-ios-success:hover:not(:disabled) {
  background-color: var(--color-success-hover);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

/* Botao danger */
.btn-ios-danger {
  background-color: var(--color-danger);
  color: var(--text-inverse);
  box-shadow: var(--shadow-sm);
}

.btn-ios-danger:hover:not(:disabled) {
  background-color: var(--color-danger-hover);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

/* Botao outline */
.btn-ios-outline {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  box-shadow: none;
}

.btn-ios-outline:hover:not(:disabled) {
  background-color: var(--color-primary-light);
}

/* Botao ghost */
.btn-ios-ghost {
  background-color: transparent;
  color: var(--color-primary);
  box-shadow: none;
}

.btn-ios-ghost:hover:not(:disabled) {
  background-color: var(--bg-hover);
}

/* Tamanhos de botao */
.btn-ios-sm {
  min-height: 36px;
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-sm);
  border-radius: var(--radius-md);
}

.btn-ios-lg {
  min-height: 52px;
  padding: var(--spacing-4) var(--spacing-8);
  font-size: var(--font-size-lg);
  border-radius: var(--radius-xl);
}

/* Botao full width */
.btn-ios-block {
  display: flex;
  width: 100%;
}

/*
==============================================================================
CARDS iOS-STYLE
==============================================================================
*/

.card-ios {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
  overflow: hidden;
}

.card-ios:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-ios-header {
  padding: var(--spacing-5) var(--spacing-6);
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
}

.card-ios-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.card-ios-body {
  padding: var(--spacing-6);
}

.card-ios-footer {
  padding: var(--spacing-5) var(--spacing-6);
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
}

/* Card compacto */
.card-ios-compact {
  border-radius: var(--radius-lg);
}

.card-ios-compact .card-ios-body {
  padding: var(--spacing-4);
}

/* Card sem hover */
.card-ios-static:hover {
  transform: none;
  box-shadow: var(--shadow-sm);
}

/*
==============================================================================
INPUTS E FORMULARIOS iOS-STYLE
==============================================================================
*/

.form-ios {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5);
}

.form-ios-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.form-ios-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  margin: 0;
}

.input-ios {
  width: 100%;
  min-height: var(--input-height);
  padding: var(--spacing-3) var(--spacing-4);
  font-family: var(--font-primary);
  font-size: var(--font-size-base);
  color: var(--text-primary);
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  outline: none;
}

.input-ios::placeholder {
  color: var(--text-tertiary);
}

.input-ios:hover {
  border-color: var(--border-color-hover);
}

.input-ios:focus {
  border-color: var(--border-color-focus);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.input-ios:disabled {
  background-color: var(--bg-tertiary);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Textarea */
.textarea-ios {
  min-height: 120px;
  resize: vertical;
  font-family: var(--font-primary);
}

/* Select */
.select-ios {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%238E8E93' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--spacing-4) center;
  padding-right: var(--spacing-10);
}

/* Estado de erro */
.input-ios.is-invalid {
  border-color: var(--color-danger);
}

.input-ios.is-invalid:focus {
  box-shadow: 0 0 0 3px var(--color-danger-light);
}

.form-ios-error {
  font-size: var(--font-size-sm);
  color: var(--color-danger);
  margin: 0;
  margin-top: var(--spacing-1);
}

/* Estado de sucesso */
.input-ios.is-valid {
  border-color: var(--color-success);
}

.input-ios.is-valid:focus {
  box-shadow: 0 0 0 3px var(--color-success-light);
}

/*
==============================================================================
BADGES iOS-STYLE
==============================================================================
*/

.badge-ios {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  line-height: 1;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.badge-ios-primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.badge-ios-success {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.badge-ios-warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.badge-ios-danger {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

.badge-ios-secondary {
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
}

/* Badge com icone */
.badge-ios .bi {
  font-size: var(--font-size-xs);
}

/*
==============================================================================
ALERTS iOS-STYLE
==============================================================================
*/

.alert-ios {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-4) var(--spacing-5);
  border-radius: var(--radius-lg);
  border-left: 4px solid;
  box-shadow: var(--shadow-sm);
}

.alert-ios-icon {
  flex-shrink: 0;
  font-size: var(--font-size-xl);
}

.alert-ios-content {
  flex: 1;
}

.alert-ios-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--spacing-1) 0;
}

.alert-ios-message {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
}

/* Variantes */
.alert-ios-success {
  background-color: var(--color-success-light);
  border-left-color: var(--color-success);
}

.alert-ios-success .alert-ios-icon {
  color: var(--color-success);
}

.alert-ios-warning {
  background-color: var(--color-warning-light);
  border-left-color: var(--color-warning);
}

.alert-ios-warning .alert-ios-icon {
  color: var(--color-warning);
}

.alert-ios-danger {
  background-color: var(--color-danger-light);
  border-left-color: var(--color-danger);
}

.alert-ios-danger .alert-ios-icon {
  color: var(--color-danger);
}

.alert-ios-info {
  background-color: var(--color-info-light);
  border-left-color: var(--color-info);
}

.alert-ios-info .alert-ios-icon {
  color: var(--color-info);
}

/*
==============================================================================
UTILITARIOS ADICIONAIS
==============================================================================
*/

/* Separador iOS */
.divider-ios {
  height: 1px;
  background-color: var(--border-color);
  border: none;
  margin: var(--spacing-6) 0;
}

/* Container com respiro */
.container-ios {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: 0 var(--spacing-4);
}

@media (min-width: 768px) {
  .container-ios {
    padding: 0 var(--spacing-6);
  }
}

/* Espacamento entre secoes */
.section-ios {
  padding: var(--spacing-8) 0;
}

@media (min-width: 768px) {
  .section-ios {
    padding: var(--spacing-12) 0;
  }
}

/* Grid iOS-style */
.grid-ios {
  display: grid;
  gap: var(--spacing-6);
}

.grid-ios-2 {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.grid-ios-3 {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.grid-ios-4 {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

/* Stack (flexbox vertical) */
.stack-ios {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

/* Group (flexbox horizontal) */
.group-ios {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

/* Loading spinner iOS */
@keyframes spin-ios {
  to {
    transform: rotate(360deg);
  }
}

.spinner-ios {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: var(--radius-full);
  animation: spin-ios 0.6s linear infinite;
}

.spinner-ios-sm {
  width: 16px;
  height: 16px;
  border-width: 1.5px;
}

.spinner-ios-lg {
  width: 32px;
  height: 32px;
  border-width: 3px;
}
'@

# Salvar arquivo
$componentsContent | Out-File -FilePath $COMPONENTS_FILE -Encoding UTF8
Write-Host "Arquivo criado: $COMPONENTS_FILE" -ForegroundColor Green
Write-Host ""

# Adicionar import no base.html
$baseHTML = Join-Path $REPO_DIR "templates\base.html"

if (Test-Path $baseHTML) {
    Write-Host "Adicionando import no base.html..." -ForegroundColor Yellow
    
    $baseContent = Get-Content $baseHTML -Raw
    
    if ($baseContent -notmatch 'components\.css') {
        $baseBackup = "$baseHTML.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item -Path $baseHTML -Destination $baseBackup
        
        # Adicionar import depois de design-tokens.css
        $baseContent = $baseContent -replace '(<link[^>]*design-tokens\.css[^>]*>)', '$1`n    <link rel="stylesheet" href="{% static ''css/components.css'' %}">'
        
        $baseContent | Out-File -FilePath $baseHTML -Encoding UTF8
        Write-Host "Import adicionado com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "Import ja existe no base.html" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  COMPONENTES CRIADOS COM SUCESSO!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Arquivo criado:" -ForegroundColor Yellow
Write-Host "  static/css/components.css" -ForegroundColor White
Write-Host ""
Write-Host "Componentes disponiveis:" -ForegroundColor Yellow
Write-Host "  - .btn-ios-primary, .btn-ios-secondary, etc" -ForegroundColor White
Write-Host "  - .card-ios, .card-ios-header, .card-ios-body" -ForegroundColor White
Write-Host "  - .input-ios, .form-ios, .select-ios" -ForegroundColor White
Write-Host "  - .badge-ios-primary, .badge-ios-success, etc" -ForegroundColor White
Write-Host "  - .alert-ios-success, .alert-ios-warning, etc" -ForegroundColor White
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "  1. Testar componentes no navegador" -ForegroundColor White
Write-Host "  2. Executar: .\04_refatorar_custom_css.ps1" -ForegroundColor White
Write-Host ""