# git-sync.ps1
# Para executar no PowerShell do VSCode:
# .\git-sync.ps1
# .\git-sync.ps1 -commitMessage "banco de dados implantado"
# Script para automatizar o envio de alterações para o GitHub

# git-sync.ps1
# Script para automatizar o envio de alterações para o GitHub

# Verifica se há mensagem de commit como parâmetro
param (
    [string]$commitMessage = "Atualização automática: $(Get-Date -Format 'dd/MM/yyyy HH:mm')",
    [string]$branchName = "main" # Branch padrão para criar se estiver detached
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
# Apenas executa o comando para verificar seu código de saída, descartando o resultado
git symbolic-ref -q HEAD > $null # <<< CORREÇÃO AQUI
$detachedHead = $LASTEXITCODE -ne 0 # Verifica o código de saída do comando anterior

if ($detachedHead) {
    Write-ColorOutput "Detectado estado de 'detached HEAD'!" $colorWarning
    $createBranchInput = Read-Host "Deseja criar e mudar para uma nova branch local para suas alterações? (S/N)"

    if ($createBranchInput -eq "S" -or $createBranchInput -eq "s") {
        $newBranchName = Read-Host "Digite o nome da nova branch (pressione Enter para usar '$branchName')"
        if ([string]::IsNullOrEmpty($newBranchName)) {
            $newBranchName = $branchName
        }

        Write-ColorOutput "Criando e mudando para a nova branch '$newBranchName'..." $colorInfo
        # Usa checkout -b para criar e mudar para a branch de uma vez
        git checkout -b $newBranchName

        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "Erro ao criar ou mudar para a nova branch!" $colorError
            exit 1
        }
        # Importante: Se criou a branch, não está mais em detached HEAD para a lógica de push
        $detachedHead = $false
        $branchName = $newBranchName # Atualiza o nome da branch a ser usada no push
    } else {
        Write-ColorOutput "Continuando em estado de detached HEAD." $colorWarning
        Write-ColorOutput "Suas alterações serão commitadas localmente, mas NÃO serão enviadas ao GitHub." $colorWarning
        Write-ColorOutput "Após o commit, crie uma branch ('git branch nome-branch') e faça checkout ('git checkout nome-branch') para poder enviar ('git push')." $colorWarning
        # Mantém $detachedHead = $true para a lógica de não fazer push
    }
} else {
     # Se não está detached, tenta obter o nome da branch atual para usar no push
     $currentBranch = git rev-parse --abbrev-ref HEAD
     if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrEmpty($currentBranch)) {
         $branchName = $currentBranch
         Write-ColorOutput "Branch atual detectada: '$branchName'" $colorInfo
     } else {
         Write-ColorOutput "Não foi possível detectar a branch atual automaticamente, usando '$branchName'." $colorWarning
     }
}


# Verifica status do Git e processa alterações
Write-ColorOutput "Verificando alterações no repositório..." $colorInfo
$status = git status --porcelain

if ([string]::IsNullOrEmpty($status)) {
    Write-ColorOutput "Nenhuma alteração detectada para commit." $colorWarning
    exit 0
}

# Mostra arquivos modificados
Write-ColorOutput "Arquivos modificados:" $colorInfo
# Usa --short para uma visão mais limpa
git status --short

# Pergunta se quer continuar
$confirma = Read-Host "Deseja adicionar e commitar essas alterações? (S/N)"
if ($confirma -ne "S" -and $confirma -ne "s") {
    Write-ColorOutput "Operação cancelada pelo usuário." $colorWarning
    exit 0
}

# Adiciona todas as alterações
Write-ColorOutput "Adicionando alterações (git add .)..." $colorInfo
git add .

# Verifica se adicionar funcionou
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "Erro ao adicionar alterações (git add .)! Verifique os arquivos." $colorError
    exit 1
}

# Faz o commit
Write-ColorOutput "Criando commit com a mensagem: '$commitMessage'" $colorInfo
git commit -m $commitMessage

# Verifica se commit funcionou
if ($LASTEXITCODE -ne 0) {
    # Pode acontecer se não houver nada para commitar após o add (raro aqui, mas possível) ou outro erro
    Write-ColorOutput "Erro ao criar commit! Verifique o status do git." $colorError
    # Verifica se foi porque não havia nada para commitar
    if (git status --porcelain) {
         # Ainda há alterações, então foi outro erro de commit
         exit 1
    } else {
         Write-ColorOutput "Aviso: Parece que não havia alterações preparadas para o commit após 'git add .'." $colorWarning
         # Decide continuar ou sair? Vamos sair para evitar push vazio.
         exit 0
    }

}

# --- Lógica de Push ---
# Só tenta fazer push se NÃO estiver em detached head (ou se criou uma branch)
if (-not $detachedHead) {
    Write-ColorOutput "Enviando alterações para o repositório remoto (origin/$branchName)..." $colorInfo
    # Usa -u para configurar o upstream na primeira vez
    git push -u origin $branchName

    # Verifica resultado final do push
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "Alterações enviadas com sucesso para origin/$branchName!" $colorSuccess
    } else {
        Write-ColorOutput "Erro ao enviar alterações para o GitHub (origin/$branchName)." $colorError
        Write-ColorOutput "Possíveis causas: conflitos, falta de permissão, branch remota inexistente." $colorWarning
        Write-ColorOutput "Tente executar manualmente: git push -u origin $branchName" $colorInfo
        # Considerar sair com erro aqui?
        # exit 1
    }
} else {
     # Mensagem se estava em detached HEAD e não criou branch
     Write-ColorOutput "Commit criado com sucesso localmente." $colorSuccess
     Write-ColorOutput "Lembre-se: As alterações NÃO foram enviadas ao GitHub pois você optou por continuar em detached HEAD." $colorWarning
     Write-ColorOutput "Para enviar, crie uma branch ('git branch nome-branch'), faça checkout ('git checkout nome-branch') e então 'git push -u origin nome-branch'." $colorInfo
}
