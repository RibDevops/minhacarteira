$ErrorActionPreference = 'Stop'

# Define o diretório de trabalho para o local onde o script está sendo executado.
# Isso garante que todos os caminhos relativos funcionem corretamente.
Set-Location $PSScriptRoot

Write-Host "`n== 1. Removendo arquivos CSS mortos (nunca carregados ou sem classes usadas) ==`n"

# Lista de arquivos CSS a serem removidos.
$cssFilesToRemove = @(
    "static/css/all.css",
    "static/css/calendar.css",
    "static/css/fontawesome.min.css",
    "static/css/simple-sidebar.css"
)

foreach ($file in $cssFilesToRemove) {
    # Tenta remover o arquivo do controle de versão do Git. 
    # Se o arquivo não estiver no Git, o comando falhará, mas continuaremos para a remoção física.
    # O '-ErrorAction SilentlyContinue' evita que erros do Git interrompam o script.
    git rm -f $file -ErrorAction SilentlyContinue
    
    # Remove fisicamente o arquivo do sistema de arquivos.
    # O '-Force' garante a remoção mesmo se o arquivo for somente leitura.
    # O '-ErrorAction SilentlyContinue' evita que erros (ex: arquivo não encontrado) interrompam o script.
    Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
    Write-Host "  - Removido: $file"
}

Write-Host "`n== 2. Removendo os <link> órfãos em templates/base.html ==`n"

$baseHtmlPath = "templates/base.html"
$backupExtension = ".bak"
$backupPath = $baseHtmlPath + $backupExtension

# Verifica se o arquivo base.html existe antes de tentar modificá-lo.
if (Test-Path $baseHtmlPath) {
    # Cria um backup do arquivo original antes de fazer as modificações.
    Copy-Item -Path $baseHtmlPath -Destination $backupPath -Force
    Write-Host "  - Backup de '$baseHtmlPath' criado em '$backupPath'"

    # Lê o conteúdo do arquivo, filtra as linhas que contêm os links CSS específicos
    # e salva o conteúdo restante de volta no arquivo original.
    $content = Get-Content $baseHtmlPath | Where-Object { 
        $_ -notmatch "css/simple-sidebar.css" -and 
        $_ -notmatch "css/fontawesome.min.css"
    }
    $content | Set-Content $baseHtmlPath
    Write-Host "  - Links CSS removidos de '$baseHtmlPath'"

    # Remove o arquivo de backup após a modificação bem-sucedida.
    Remove-Item -Path $backupPath -Force -ErrorAction SilentlyContinue
    Write-Host "  - Backup '$backupPath' removido."
} else {
    Write-Warning "  - Arquivo '$baseHtmlPath' não encontrado. Pulando esta etapa."
}

Write-Host "`n== 3. Parando de versionar staticfiles/ (é output de collectstatic, não código-fonte) ==`n"

$staticfilesDir = "staticfiles/"
$gitIgnorePath = ".gitignore"

# Verifica se o diretório 'staticfiles/' está sendo rastreado pelo Git.
# Se estiver, ele é removido do índice do Git (mas não fisicamente).
if (git ls-files $staticfilesDir --error-unmatch -ErrorAction SilentlyContinue) {
    git rm -r --cached $staticfilesDir -ErrorAction SilentlyContinue
    Write-Host "  - Diretório '$staticfilesDir' removido do controle de versão do Git."
} else {
    Write-Host "  - Diretório '$staticfilesDir' não está sendo rastreado pelo Git (ou já foi removido)."
}

# Verifica se 'staticfiles/' já está listado no .gitignore.
# Se não estiver, adiciona-o para evitar que seja rastreado no futuro.
if (-not (Select-String -Path $gitIgnorePath -Pattern $staticfilesDir -Quiet -ErrorAction SilentlyContinue)) {
    Add-Content -Path $gitIgnorePath -Value $staticfilesDir
    Write-Host "  - '$staticfilesDir' adicionado ao '$gitIgnorePath'."
} else {
    Write-Host "  - '$staticfilesDir' já está no '$gitIgnorePath'."
}

Write-Host "`n== Concluído. Revise antes de commitar: ==`n"
# Exibe o status atual do Git para que o usuário possa revisar as alterações.
git status --short

Write-Host "`nScript concluído. Por favor, revise as alterações com 'git status' e 'git diff' antes de commitar.`n"
