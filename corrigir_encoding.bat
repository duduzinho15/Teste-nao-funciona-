@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo  CORREÇÃO DE ENCODING - APOSTAPRO
echo ===================================================
echo.
echo Este script irá guiá-lo pelo processo de correção de encoding.
echo Certifique-se de ter privilégios de administrador.
echo.

:: Verificar se está sendo executado como administrador
net session >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo [INFO] Executando como administrador.
) else (
    echo [ERRO] Este script precisa ser executado como administrador.
    echo [ERRO] Clique com o botão direito no arquivo e selecione "Executar como administrador".
    pause
    exit /b 1
)

:: Configurações
set PG_BIN="C:\Program Files\PostgreSQL\17\bin"
set PG_DATA="C:\Program Files\PostgreSQL\17\data"
set PG_SERVICE=postgresql-x64-17
set PGPASSWORD=Canjica@@2025

:: Menu principal
:menu
cls
echo ===================================================
echo  MENU PRINCIPAL - CORREÇÃO DE ENCODING
echo ===================================================
echo.
echo 1. Redefinir senha do PostgreSQL
echo 2. Criar novo banco com encoding UTF-8
echo 3. Exportar e importar dados
echo 4. Verificar e corrigir encoding dos dados
echo 5. Verificar configurações atuais
echo 6. Sair
echo.
set /p opcao="Escolha uma opção (1-6): "

echo.

if "%opcao%"=="1" goto reset_password
if "%opcao%"=="2" goto create_db
if "%opcao%"=="3" goto export_import
if "%cao%"=="4" goto fix_data
if "%opcao%"=="5" goto check_config
if "%opcao%"=="6" goto end

goto menu

:reset_password
echo [ETAPA 1/4] Redefinindo senha do PostgreSQL...
call :run_ps1 reset_password.ps1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao redefinir a senha.
    pause
    goto menu
)
echo.
echo [SUCESSO] Senha redefinida com sucesso para 'Canjica@@2025'
pause
goto menu

:create_db
echo [ETAPA 2/4] Criando novo banco de dados com encoding UTF-8...
"%PG_BIN%\psql.exe" -U postgres -f criar_banco_utf8.sql
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao criar o banco de dados.
    pause
    goto menu
)
echo.
echo [SUCESSO] Banco de dados 'apostapro_utf8' criado com sucesso!
pause
goto menu

:export_import
echo [ETAPA 3/4] Exportando e importando dados...
call exportar_importar_dados.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao exportar/importar dados.
    pause
    goto menu
)
echo.
echo [SUCESSO] Dados exportados e importados com sucesso!
pause
goto menu

:fix_data
echo [ETAPA 4/4] Verificando e corrigindo dados...
python corrigir_dados.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Ocorreram erros durante a correção dos dados.
    echo [INFO] Verifique o arquivo 'correcao_encoding.log' para mais detalhes.
    pause
    goto menu
)
echo.
echo [SUCESSO] Verificação e correção de dados concluídas!
pause
goto menu

:check_config
echo [INFO] Verificando configurações atuais...
python verificar_encoding.py
pause
goto menu

:run_ps1
powershell -ExecutionPolicy Bypass -File "%~1"
if %ERRORLEVEL% NEQ 0 (
    exit /b 1
)
exit /b 0

:end
echo.
echo ===================================================
echo  PROCESSO CONCLUÍDO!
echo  Verifique os logs gerados para mais detalhes.
echo  Não se esqueça de atualizar a configuração da
echo  aplicação para usar o novo banco de dados.
echo ===================================================
echo.
pause
