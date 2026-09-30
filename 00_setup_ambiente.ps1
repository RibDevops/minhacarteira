# ==============================================================================
# BLOCO 0 - SCRIPT 1: SETUP DO AMBIENTE E VALIDACAO (COMPATIVEL PS 5.1)
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  MINHACARTEIRA - SETUP DO AMBIENTE" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

$REPO_URL      = "https://github.com/RibDevops/minhacarteira.git"
$PROJECT_NAME  = "minhacarteira"
$SCRIPT_DIR    = $PSScriptRoot
$LOG_FILE      = Join-Path $SCRIPT_DIR ("setup_log_{0}.txt" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

function Write-Log {
    param(
        [Parameter(Mandatory=$true)][string]$Message,
        [ValidateSet("INFO","SUCCESS","WARNING","ERROR")][string]$Type = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[{0}] [{1}] {2}" -f $timestamp, $Type, $Message

    switch ($Type) {
        "SUCCESS" { Write-Host $Message -ForegroundColor Green }
        "WARNING" { Write-Host $Message -ForegroundColor Yellow }
        "ERROR"   { Write-Host $Message -ForegroundColor Red }
        default   { Write-Host $Message -ForegroundColor White }
    }

    $line | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
}

function Assert-Command {
    param(
        [Parameter(Mandatory=$true)][string]$Command,
        [Parameter(Mandatory=$true)][string]$FriendlyName,
        [string]$InstallHint = ""
    )

    $cmd = Get-Command $Command -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Log ("ERRO: {0} nao encontrado. {1}" -f $FriendlyName, $InstallHint) "ERROR"
        exit 1
    }

    $ver = ""
    if ($Command -eq "java") {
        # java -version escreve em stderr; capturamos redirecionando tudo para variavel
        $ver = (& java -version 2>&1 | Out-String).Trim().Split([Environment]::NewLine)[0]
    } elseif ($Command -eq "mvn") {
        $ver = (& mvn -v 2>&1 | Select-Object -First 1)
    } else {
        $ver = (& $Command --version 2>&1 | Select-Object -First 1)
    }

    if (-not $ver) { $ver = "(versao nao detectada)" }
    Write-Log ("OK: {0} encontrado: {1}" -f $FriendlyName, $ver) "SUCCESS"
}

# ==============================================================================
# 1) REQUISITOS
# ==============================================================================
Write-Log "ETAPA 1: VERIFICACAO DE REQUISITOS" "INFO"

Assert-Command git  "Git"   "Instale em https://git-scm.com/download/win"
Assert-Command java "Java"  "Instale Java 17+ em https://adoptium.net/"
Assert-Command mvn  "Maven" "Instale em https://maven.apache.org/download.cgi"

# Checagem simples de versao do Java (major >= 17)
$javaLine = (& java -version 2>&1 | Out-String).Trim().Split([Environment]::NewLine)[0]

$major = $null
if ($javaLine -match '"?(\d+)\.?') {
    $major = [int]$matches[1]
}

if ($major -ne $null -and $major -ge 17) {
    Write-Log ("OK: Java major >= 17 detectado (versao: {0})" -f $javaLine) "SUCCESS"
} else {
    Write-Log ("ATENCAO: Nao consegui confirmar Java 17+. Linha: {0}" -f $javaLine) "WARNING"
}

Write-Host ""

# ==============================================================================
# 2) REPOSITORIO (detecta se ja esta dentro do repo)
# ==============================================================================
Write-Log "ETAPA 2: REPOSITORIO" "INFO"

$BASE_DIR = $null

if (Test-Path (Join-Path $SCRIPT_DIR ".git")) {
    $BASE_DIR = $SCRIPT_DIR
    Write-Log ("Repo ja presente no diretorio do script: {0}" -f $BASE_DIR) "INFO"
} else {
    $BASE_DIR = Join-Path $SCRIPT_DIR $PROJECT_NAME

    if (-not (Test-Path $BASE_DIR)) {
        Write-Log ("Clonando repo em: {0}" -f $BASE_DIR) "INFO"
        $out = & git clone $REPO_URL $BASE_DIR 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "ERRO ao clonar repositorio. Saida:" "ERROR"
            $out | Out-Host
            exit 1
        }
        Write-Log "OK: repositorio clonado" "SUCCESS"
    } else {
        if (Test-Path (Join-Path $BASE_DIR ".git")) {
            Write-Log ("Repo encontrado em {0}. Pulando clonagem." -f $BASE_DIR) "INFO"
        } else {
            Write-Log ("ATENCAO: Pasta {0} existe, mas nao parece repo Git." -f $BASE_DIR) "WARNING"
        }
    }
}

Write-Host ""

# ==============================================================================
# 3) ESTRUTURA ESPERADA
# ==============================================================================
Write-Log "ETAPA 3: VALIDACAO DE ESTRUTURA" "INFO"

$expected = @(
    "pom.xml",
    "src\main\java",
    "src\main\resources",
    "src\test\java"
)

$missing = @()
foreach ($rel in $expected) {
    $full = Join-Path $BASE_DIR $rel
    if (Test-Path $full) {
        Write-Log ("OK: encontrado {0}" -f $rel) "SUCCESS"
    } else {
        Write-Log ("ERRO: nao encontrado {0}" -f $rel) "ERROR"
        $missing += $rel
    }
}

if ($missing.Count -gt 0) {
    Write-Log ("ATENCAO: itens ausentes: {0}" -f ($missing -join ", ")) "WARNING"
}

Write-Host ""

# ==============================================================================
# 4) POM.XML (dependencias)
# ==============================================================================
Write-Log "ETAPA 4: ANALISE DO pom.xml" "INFO"

$pomPath = Join-Path $BASE_DIR "pom.xml"
if (-not (Test-Path $pomPath)) {
    Write-Log "ERRO: pom.xml nao encontrado." "ERROR"
    exit 1
}

[xml]$pom = Get-Content -Path $pomPath

$projVersion = $pom.project.version
if (-not $projVersion) { $projVersion = "(nao informada)" }
Write-Log ("Versao do projeto: {0}" -f $projVersion) "INFO"

$springBoot = $pom.project.parent.version
if ($springBoot) {
    Write-Log ("Spring Boot (parent): {0}" -f $springBoot) "INFO"
}

$deps = $pom.project.dependencies.dependency
$depCount = 0
if ($deps) { $depCount = $deps.Count }
Write-Log ("Total de dependencias: {0}" -f $depCount) "INFO"

if ($depCount -gt 0) {
    foreach ($d in $deps) {
        $gid = $d.groupId
        $aid = $d.artifactId
        $ver = $d.version
        if (-not $ver) { $ver = "(herdada)" }
        Write-Log (" - {0}:{1} {2}" -f $gid, $aid, $ver) "INFO"
    }
}

Write-Host ""

# ==============================================================================
# 5) BUILD
# ==============================================================================
Write-Log "ETAPA 5: BUILD (mvn clean compile)" "INFO"
Push-Location $BASE_DIR

Write-Host "Executando Maven... (pode demorar na primeira vez)" -ForegroundColor Yellow
$outBuild = & mvn clean compile 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Log "ERRO: build falhou. Saida do Maven:" "ERROR"
    $outBuild | Out-Host
    Pop-Location
    exit 1
}
Write-Log "OK: build executado com sucesso." "SUCCESS"

Write-Host ""

# ==============================================================================
# 6) TESTES
# ==============================================================================
Write-Log "ETAPA 6: TESTES (mvn test)" "INFO"
Write-Host "Executando testes..." -ForegroundColor Yellow
$outTest = & mvn test 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Log "ATENCAO: testes falharam. Saida:" "WARNING"
    $outTest | Out-Host
} else {
    Write-Log "OK: testes executados com sucesso." "SUCCESS"
}

Pop-Location
Write-Host ""

# ==============================================================================
# 7) CONTAGEM RAPIDA DE ARQUIVOS
# ==============================================================================
Write-Log "ETAPA 7: CONTAGEM RAPIDA" "INFO"

$javaMain = @(Get-ChildItem -Path (Join-Path $BASE_DIR "src\main") -Filter "*.java" -Recurse -ErrorAction SilentlyContinue)
$javaTest = @(Get-ChildItem -Path (Join-Path $BASE_DIR "src\test") -Filter "*.java" -Recurse -ErrorAction SilentlyContinue)
Write-Log ("Java (src/main): {0}" -f $javaMain.Count) "INFO"
Write-Log ("Java (src/test): {0}" -f $javaTest.Count) "INFO"

$static = Join-Path $BASE_DIR "src\main\resources\static"
if (Test-Path $static) {
    $html = @(Get-ChildItem -Path $static -Filter "*.html" -Recurse -ErrorAction SilentlyContinue)
    $css  = @(Get-ChildItem -Path $static -Filter "*.css"  -Recurse -ErrorAction SilentlyContinue)
    $js   = @(Get-ChildItem -Path $static -Filter "*.js"   -Recurse -ErrorAction SilentlyContinue)
    Write-Log ("Static HTML: {0}" -f $html.Count) "INFO"
    Write-Log ("Static CSS : {0}" -f $css.Count)  "INFO"
    Write-Log ("Static JS  : {0}" -f $js.Count)   "INFO"
} else {
    Write-Log "ATENCAO: pasta static nao encontrada (src/main/resources/static)." "WARNING"
}

Write-Host ""

# ==============================================================================
# FINAL
# ==============================================================================
Write-Log "FINAL: Setup concluido." "SUCCESS"
Write-Log ("Projeto base: {0}" -f $BASE_DIR) "INFO"
Write-Log ("Log salvo em: {0}" -f $LOG_FILE) "INFO"

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  SETUP CONCLUIDO" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Revise o log: $LOG_FILE" -ForegroundColor White
Write-Host "2. Execute: .\00_criar_backup.ps1" -ForegroundColor White
Write-Host "3. Execute: .\00_criar_branch.ps1" -ForegroundColor White