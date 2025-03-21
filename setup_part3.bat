@echo off
echo Configurando Parte 3 do Sistema DISC...

rem Verificar e criar diretórios necessários
if not exist "c:\pyp\sdisc\static\js" mkdir c:\pyp\sdisc\static\js
if not exist "c:\pyp\sdisc\static\css" mkdir c:\pyp\sdisc\static\css
if not exist "c:\pyp\sdisc\templates" mkdir c:\pyp\sdisc\templates
if not exist "c:\pyp\sdisc\models" mkdir c:\pyp\sdisc\models

rem Criar arquivos do questionário DISC
echo Criando arquivo de dados do questionário...
echo // Dados do questionário DISC > c:\pyp\sdisc\static\js\disc_questions.js

rem Criar arquivo para o algoritmo de pontuação
echo Criando arquivo para o algoritmo de pontuação...
echo // Algoritmo de pontuação DISC > c:\pyp\sdisc\static\js\disc_scoring.js

rem Criar template para o questionário
echo Criando template para o questionário...
echo <!-- Template do Questionário DISC --> > c:\pyp\sdisc\templates\quiz.html

rem Criar modelo para resultados
echo Criando modelo para resultados...
echo # Modelo para resultados DISC > c:\pyp\sdisc\models\results.py

rem Criar arquivo CSS para o questionário
echo Criando arquivo CSS para o questionário...
echo /* Estilos para o questionário DISC */ > c:\pyp\sdisc\static\css\quiz.css

echo Configuração concluída com sucesso!