# git-sync.ps1
# Para executar no PowerShell do VSCode:
# .\git-sync.ps1
# .\git-sync.ps1 -commitMessage "progresso"
# Script para automatizar o envio de alterações para o GitHub

# Verifica se há mensagem de commit como parâmetro
# git-sync.ps1
# Script para automatizar o envio de alterações para o GitHub

# Verifica se há mensagem de commit como parâmetro
param (
    [string]$commitMessage = "Atualização automática: $(Get-Date -Format 'dd/MM/yyyy HH:mm')",
    [string]$branchName = "main"
)

# Cores para feedback visual
$colorInfo = "Cyan"
$colorSuccess = "Green"
$colorWarning = "Yellow"
$colorError = "Red"

# Função para exibir mensagens coloridas
function Write-ColorOutput {
    param(
        [string]$message,
        [string]$color
    )
    Write-Host $message -ForegroundColor $color
}

# Verifica se estamos em um repositório Git
if (-not (Test-Path ".git")) {
    Write-ColorOutput "Erro: Diretório atual não é um repositório Git!" $colorError
    exit 1
}

# Verifica se estamos em detached HEAD state
$headRef = git symbolic-ref -q HEAD
$detachedHead = $LASTEXITCODE -ne 0

if ($detachedHead) {
    Write-ColorOutput "Detectado estado de 'detached HEAD'!" $colorWarning
    $createBranch = Read-Host "Deseja criar uma nova branch para suas alterações? (S/N)"
    
    if ($createBranch -eq "S" -or $createBranch -eq "s") {
        $newBranchName = Read-Host "Digite o nome da nova branch (ou pressione Enter para usar '$branchName')"
        if ([string]::IsNullOrEmpty($newBranchName)) {
            $newBranchName = $branchName
        }
        
        Write-ColorOutput "Criando nova branch '$newBranchName'..." $colorInfo
        git checkout -b $newBranchName
        
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "Erro ao criar nova branch!" $colorError
            exit 1
        }
    } else {
        Write-ColorOutput "Continuando em estado de detached HEAD." $colorWarning
        Write-ColorOutput "Suas alterações serão commitadas, mas não enviadas ao GitHub." $colorWarning
    }
}

# Verifica status do Git e processa alterações
Write-ColorOutput "Verificando alterações no repositório..." $colorInfo
$status = git status --porcelain

if ([string]::IsNullOrEmpty($status)) {
    Write-ColorOutput "Nenhuma alteração detectada." $colorWarning
    exit 0
}

# Mostra arquivos modificados
Write-ColorOutput "Arquivos modificados:" $colorInfo
git status --short

# Pergunta se quer continuar
$confirma = Read-Host "Deseja enviar essas alterações para o GitHub? (S/N)"
if ($confirma -ne "S" -and $confirma -ne "s") {
    Write-ColorOutput "Operação cancelada pelo usuário." $colorWarning
    exit 0
}

# Adiciona todas as alterações
Write-ColorOutput "Adicionando alterações..." $colorInfo
git add .

# Verifica se adicionar funcionou
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "Erro ao adicionar alterações!" $colorError
    exit 1
}

# Faz o commit
Write-ColorOutput "Criando commit: '$commitMessage'" $colorInfo
git commit -m $commitMessage

# Verifica se commit funcionou
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "Erro ao criar commit!" $colorError
    exit 1
}

# Se estiver em detached HEAD e não tiver criado branch, avisa e sai
if ($detachedHead -and ($createBranch -ne "S" -and $createBranch -ne "s")) {
    Write-ColorOutput "Commit criado com sucesso, mas não será enviado ao GitHub pois você está em um estado de detached HEAD." $colorWarning
    Write-ColorOutput "Para enviar as alterações, execute:" $colorInfo
    Write-ColorOutput "git branch nome-da-branch" $colorInfo
    Write-ColorOutput "git checkout nome-da-branch" $colorInfo
    Write-ColorOutput "git push -u origin nome-da-branch" $colorInfo
    exit 0
}

# Envia para o GitHub
Write-ColorOutput "Enviando alterações para o GitHub..." $colorInfo
git push -u origin HEAD

# Verifica resultado final
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput "Todas as alterações foram enviadas com sucesso!" $colorSuccess
} else {
    Write-ColorOutput "Erro ao enviar alterações para o GitHub." $colorError
    Write-ColorOutput "Tente executar manualmente:" $colorInfo
    Write-ColorOutput "git push -u origin HEAD" $colorInfo
}