@echo off
echo ===== Iniciando deploy do sistema DISC =====

:: Verificar ambiente Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERRO: Python nao encontrado. Instale Python 3.12 ou superior.
    exit /b 1
)

:: Verificar se estamos no diretório correto
if not exist "backend\app.py" (
    echo ERRO: Execute este script no diretorio raiz do projeto.
    exit /b 1
)

:: Verificar ambiente virtual
if not exist "venv\" (
    echo Criando ambiente virtual...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo ERRO: Falha ao criar ambiente virtual.
        exit /b 1
    )
)

:: Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

:: Instalar dependências
echo Instalando dependencias...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERRO: Falha ao instalar dependencias.
    exit /b 1
)

:: Executar testes
echo Executando testes...
python -m pytest
if %ERRORLEVEL% neq 0 (
    echo AVISO: Alguns testes falharam. Deseja continuar mesmo assim? (S/N)
    set /p continuar=
    if /i "%continuar%" neq "S" (
        echo Deploy cancelado pelo usuario.
        exit /b 1
    )
)

:: Verificar configuração de produção
if not exist "prod_config.py" (
    echo ERRO: Arquivo prod_config.py nao encontrado.
    echo Criando arquivo de configuracao de producao padrao...
    (
        echo SECRET_KEY = 'minha-chave-secreta-para-producao-mude-isso'
        echo DEBUG = False
        echo ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'seudominio.com']
        echo DATABASE_URL = 'sqlite:///app.db'
    ) > prod_config.py
    echo Arquivo prod_config.py criado. Edite-o com as configuracoes corretas antes de continuar.
    exit /b 1
)

:: Configurar banco de dados de produção
echo Configurando banco de dados...
python -c "from backend.app import db; db.create_all()"
if %ERRORLEVEL% neq 0 (
    echo ERRO: Falha ao configurar banco de dados.
    exit /b 1
)

:: Verificar frontend (para futura implementação completa com React)
echo Verificando frontend...
if exist "frontend\package.json" (
    echo Build de frontend detectado. Deseja compilar o frontend? (S/N)
    set /p build_frontend=
    if /i "%build_frontend%" equ "S" (
        cd frontend
        echo Instalando dependencias do frontend...
        npm install
        if %ERRORLEVEL% neq 0 (
            echo ERRO: Falha ao instalar dependencias do frontend.
            cd ..
            exit /b 1
        )
        echo Compilando frontend...
        npm run build
        if %ERRORLEVEL% neq 0 (
            echo ERRO: Falha ao compilar frontend.
            cd ..
            exit /b 1
        )
        cd ..
    )
)

:: Iniciar servidor em modo de produção
echo ===== Deploy concluido com sucesso! =====
echo Para iniciar o servidor em modo de producao, execute:
echo python -m backend.app --prod
echo.
echo Ou para iniciar em modo de desenvolvimento:
echo python -m backend.app
echo.

:: Opção para iniciar o servidor imediatamente
echo Deseja iniciar o servidor agora? (S/N)
set /p iniciar=
if /i "%iniciar%" equ "S" (
    echo Iniciando servidor em modo de producao...
    python -m backend.app --prod
)

exit /b 0
