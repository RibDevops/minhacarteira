# ==============================================================================
# BLOCO 1 - ANALISE COMPLETA DO CSS ATUAL
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  ANALISE COMPLETA DO CSS - MINHACARTEIRA" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_DIR = $PSScriptRoot
$STATIC_DIR = Join-Path $REPO_DIR "static"
$TEMPLATES_DIR = Join-Path $REPO_DIR "templates"
$REPORT_FILE = Join-Path $REPO_DIR "CSS_AUDIT_REPORT.md"

$report = @()

function Add-Report {
    param([string]$Text)
    $script:report += $Text
    Write-Host $Text
}

Add-Report "# AUDITORIA CSS - MINHACARTEIRA"
Add-Report ""
Add-Report "**Data:** $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')"
Add-Report ""
Add-Report "---"
Add-Report ""

# ==============================================================================
# 1) INVENTARIO DE ARQUIVOS CSS
# ==============================================================================
Add-Report "## 1. INVENTARIO DE ARQUIVOS CSS"
Add-Report ""

$cssFiles = Get-ChildItem -Path $STATIC_DIR -Filter "*.css" -Recurse -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch '\\node_modules\\|\\venv\\|\\.git\\' }

Add-Report "**Total de arquivos CSS:** $($cssFiles.Count)"
Add-Report ""
Add-Report "### Arquivos encontrados:"
Add-Report ""

$customCSS = @()
$vendorCSS = @()
$adminCSS = @()

foreach ($file in $cssFiles) {
    $relativePath = $file.FullName.Replace($REPO_DIR, "").TrimStart('\')
    $sizeKB = [math]::Round($file.Length / 1KB, 2)
    
    if ($relativePath -match "\\vendor\\") {
        $vendorCSS += $file
        Add-Report "- [VENDOR] ``$relativePath`` ($sizeKB KB)"
    } elseif ($relativePath -match "\\admin\\") {
        $adminCSS += $file
        Add-Report "- [ADMIN] ``$relativePath`` ($sizeKB KB)"
    } else {
        $customCSS += $file
        Add-Report "- [CUSTOM] ``$relativePath`` ($sizeKB KB)"
    }
}

Add-Report ""
Add-Report "**Resumo:**"
Add-Report "- Custom (nosso codigo): $($customCSS.Count)"
Add-Report "- Vendor (bibliotecas externas): $($vendorCSS.Count)"
Add-Report "- Admin Django: $($adminCSS.Count)"
Add-Report ""

# ==============================================================================
# 2) ANALISE DOS CSS CUSTOMIZADOS
# ==============================================================================
Add-Report "---"
Add-Report ""
Add-Report "## 2. ANALISE DOS CSS CUSTOMIZADOS"
Add-Report ""

foreach ($file in $customCSS) {
    $relativePath = $file.FullName.Replace($REPO_DIR, "").TrimStart('\')
    $content = Get-Content $file.FullName -Raw
    $lines = ($content -split "`n").Count
    $sizeKB = [math]::Round($file.Length / 1KB, 2)
    
    Add-Report "### ``$relativePath``"
    Add-Report ""
    Add-Report "- **Tamanho:** $sizeKB KB"
    Add-Report "- **Linhas:** $lines"
    Add-Report ""
    
    # Contar seletores
    $selectors = ([regex]::Matches($content, '\{[^}]*\}')).Count
    Add-Report "- **Seletores CSS:** aprox. $selectors"
    Add-Report ""
    
    # Detectar variaveis CSS
    $cssVars = [regex]::Matches($content, '--[\w-]+')
    if ($cssVars.Count -gt 0) {
        Add-Report "- **Variaveis CSS:** $($cssVars.Count) encontradas [OK]"
        Add-Report ""
    } else {
        Add-Report "- **Variaveis CSS:** Nenhuma encontrada [ATENCAO]"
        Add-Report ""
    }
    
    # Detectar media queries
    $mediaQueries = ([regex]::Matches($content, '@media')).Count
    Add-Report "- **Media Queries:** $mediaQueries"
    Add-Report ""
    
    # Detectar cores hardcoded
    $colorsHex = [regex]::Matches($content, '#[0-9a-fA-F]{3,6}')
    $colorsRgb = [regex]::Matches($content, 'rgba?\([^)]+\)')
    $totalColors = $colorsHex.Count + $colorsRgb.Count
    
    if ($totalColors -gt 0) {
        Add-Report "- **Cores hardcoded:** $totalColors [ATENCAO]"
        Add-Report "  - HEX: $($colorsHex.Count)"
        Add-Report "  - RGB/RGBA: $($colorsRgb.Count)"
        Add-Report ""
    }
    
    # Detectar !important
    $importants = ([regex]::Matches($content, '!important')).Count
    if ($importants -gt 0) {
        Add-Report "- **!important encontrados:** $importants [ATENCAO]"
        Add-Report ""
    }
    
    # Detectar box-shadow
    $shadows = ([regex]::Matches($content, 'box-shadow:')).Count
    Add-Report "- **Sombras (box-shadow):** $shadows"
    Add-Report ""
    
    # Detectar border-radius
    $borderRadius = ([regex]::Matches($content, 'border-radius:')).Count
    Add-Report "- **Border-radius:** $borderRadius"
    Add-Report ""
    
    Add-Report ""
}

# ==============================================================================
# 3) ANALISE DE USO NOS TEMPLATES
# ==============================================================================
Add-Report "---"
Add-Report ""
Add-Report "## 3. ANALISE DE USO NOS TEMPLATES"
Add-Report ""

$htmlFiles = Get-ChildItem -Path $TEMPLATES_DIR -Filter "*.html" -Recurse -ErrorAction SilentlyContinue

Add-Report "**Total de templates HTML:** $($htmlFiles.Count)"
Add-Report ""

# Detectar classes CSS mais usadas
$allClasses = @{}

foreach ($html in $htmlFiles) {
    $content = Get-Content $html.FullName -Raw
    $classes = [regex]::Matches($content, 'class="([^"]+)"')
    
    foreach ($match in $classes) {
        $classList = $match.Groups[1].Value -split '\s+'
        foreach ($cls in $classList) {
            if ($cls -and $cls.Trim()) {
                if ($allClasses.ContainsKey($cls)) {
                    $allClasses[$cls]++
                } else {
                    $allClasses[$cls] = 1
                }
            }
        }
    }
}

Add-Report "### Top 20 classes CSS mais usadas:"
Add-Report ""

$topClasses = $allClasses.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 20

foreach ($class in $topClasses) {
    Add-Report "- ``$($class.Key)`` usado $($class.Value)x"
}

Add-Report ""

# ==============================================================================
# 4) PROBLEMAS IDENTIFICADOS
# ==============================================================================
Add-Report "---"
Add-Report ""
Add-Report "## 4. PROBLEMAS IDENTIFICADOS"
Add-Report ""

$problems = @()

# Verificar ausencia de design tokens
$hasTokens = $false
foreach ($file in $customCSS) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match ':root\s*\{') {
        $hasTokens = $true
        break
    }
}

if (-not $hasTokens) {
    $problems += "[ATENCAO] Nao ha design tokens (variaveis CSS em :root)"
}

# Verificar cores hardcoded
$totalHardcodedColors = 0
foreach ($file in $customCSS) {
    $content = Get-Content $file.FullName -Raw
    $totalHardcodedColors += ([regex]::Matches($content, '#[0-9a-fA-F]{3,6}|rgba?\([^)]+\)')).Count
}

if ($totalHardcodedColors -gt 20) {
    $problems += "[ATENCAO] Muitas cores hardcoded ($totalHardcodedColors) - dificulta manutencao"
}

# Verificar !important
$totalImportants = 0
foreach ($file in $customCSS) {
    $content = Get-Content $file.FullName -Raw
    $totalImportants += ([regex]::Matches($content, '!important')).Count
}

if ($totalImportants -gt 10) {
    $problems += "[ATENCAO] Uso excessivo de !important ($totalImportants) - indica problemas de especificidade"
}

# Verificar tamanho total
$totalSizeKB = [math]::Round(($customCSS | Measure-Object -Property Length -Sum).Sum / 1KB, 2)
if ($totalSizeKB -gt 100) {
    $problems += "[ATENCAO] CSS customizado muito grande ($totalSizeKB KB) - considerar minificacao"
}

if ($problems.Count -gt 0) {
    foreach ($p in $problems) {
        Add-Report $p
        Add-Report ""
    }
} else {
    Add-Report "[OK] Nenhum problema critico identificado"
    Add-Report ""
}

# ==============================================================================
# 5) OPORTUNIDADES DE MELHORIA
# ==============================================================================
Add-Report "---"
Add-Report ""
Add-Report "## 5. OPORTUNIDADES DE MELHORIA"
Add-Report ""

Add-Report "### 5.1 Design System iOS-style"
Add-Report ""
Add-Report "- [ ] Criar arquivo design-tokens.css com variaveis CSS"
Add-Report "- [ ] Definir paleta de cores (primaria, secundaria, backgrounds, textos)"
Add-Report "- [ ] Definir escala de espacamentos (4px, 8px, 12px, 16px, 24px, 32px, 48px)"
Add-Report "- [ ] Definir escala tipografica (font-size, line-height, font-weight)"
Add-Report "- [ ] Definir sombras padronizadas (iOS-style: suaves e discretas)"
Add-Report "- [ ] Definir border-radius padrao (8px, 12px, 16px)"
Add-Report ""

Add-Report "### 5.2 Refatoracao CSS"
Add-Report ""
Add-Report "- [ ] Migrar cores hardcoded para variaveis CSS"
Add-Report "- [ ] Criar components.css (botoes, cards, inputs, badges)"
Add-Report "- [ ] Criar utilities.css (margin, padding, display, text-align)"
Add-Report "- [ ] Integrar dark-mode usando variaveis CSS"
Add-Report "- [ ] Remover !important desnecessarios"
Add-Report "- [ ] Consolidar seletores duplicados"
Add-Report ""

Add-Report "### 5.3 Modernizacao Visual (iOS-style)"
Add-Report ""
Add-Report "- [ ] Aplicar border-radius: 12px em cards e containers"
Add-Report "- [ ] Aplicar sombras suaves (box-shadow: 0 2px 8px rgba(0,0,0,0.08))"
Add-Report "- [ ] Usar tipografia moderna (system-ui, -apple-system, SF Pro Display)"
Add-Report "- [ ] Implementar estados hover/focus/active refinados"
Add-Report "- [ ] Adicionar transicoes suaves (transition: all 0.2s ease)"
Add-Report "- [ ] Usar cores suaves e gradientes sutis"
Add-Report "- [ ] Melhorar espacamentos (mais respiro, menos compactacao)"
Add-Report ""

Add-Report "### 5.4 Responsividade"
Add-Report ""
Add-Report "- [ ] Revisar breakpoints mobile (< 768px)"
Add-Report "- [ ] Melhorar layout do dashboard em mobile"
Add-Report "- [ ] Ajustar formularios para telas pequenas"
Add-Report "- [ ] Testar em iOS Safari e Android Chrome"
Add-Report ""

Add-Report "### 5.5 Performance"
Add-Report ""
Add-Report "- [ ] Minificar CSS customizado"
Add-Report "- [ ] Remover CSS nao utilizado (PurgeCSS)"
Add-Report "- [ ] Usar apenas vendor CSS necessario"
Add-Report ""

# ==============================================================================
# 6) PLANO DE REFATORACAO
# ==============================================================================
Add-Report "---"
Add-Report ""
Add-Report "## 6. PLANO DE REFATORACAO"
Add-Report ""

Add-Report "### BLOCO 2: Design Tokens"
Add-Report "- Criar static/css/design-tokens.css"
Add-Report "- Definir todas as variaveis CSS (:root)"
Add-Report "- Testar em um componente isolado"
Add-Report ""

Add-Report "### BLOCO 3: Componentes Base"
Add-Report "- Criar static/css/components.css"
Add-Report "- Refatorar botoes"
Add-Report "- Refatorar cards"
Add-Report "- Refatorar inputs/forms"
Add-Report "- Refatorar badges/tags"
Add-Report ""

Add-Report "### BLOCO 4: Modernizacao Visual"
Add-Report "- Aplicar design tokens em custom.css"
Add-Report "- Ajustar border-radius, sombras, espacamentos"
Add-Report "- Melhorar tipografia"
Add-Report "- Refinar estados interativos"
Add-Report ""

Add-Report "### BLOCO 5: Dark Mode Integrado"
Add-Report "- Migrar dark-mode.css para variaveis CSS"
Add-Report "- Criar toggle dark/light"
Add-Report "- Testar todos os componentes"
Add-Report ""

Add-Report "### BLOCO 6: Responsividade"
Add-Report "- Ajustar breakpoints"
Add-Report "- Melhorar mobile-first"
Add-Report "- Testar em dispositivos reais"
Add-Report ""

# ==============================================================================
# SALVAR RELATORIO
# ==============================================================================
Add-Report "---"
Add-Report ""
Add-Report "## 7. PROXIMOS PASSOS"
Add-Report ""
Add-Report "Execute o script de refatoracao:"
Add-Report ""
Add-Report "``````powershell"
Add-Report ".\02_criar_design_tokens.ps1"
Add-Report "``````"
Add-Report ""

Write-Host ""
Write-Host "Salvando relatorio em: $REPORT_FILE" -ForegroundColor Yellow

$report | Out-File -FilePath $REPORT_FILE -Encoding UTF8

Write-Host "Relatorio salvo com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Para visualizar:" -ForegroundColor Yellow
Write-Host "  notepad $REPORT_FILE" -ForegroundColor Gray
Write-Host ""
Write-Host "Proximo passo:" -ForegroundColor Yellow
Write-Host "  .\02_criar_design_tokens.ps1" -ForegroundColor White
Write-Host ""