@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo  EXPORTACAO E IMPORTACAO DE DADOS - APOSTAPRO
echo ===================================================
echo.

:: Configuracoes
set PGPASSWORD=Canjica@@2025
set "PG_BIN=C:\Program Files\PostgreSQL\17\bin"
set HOST=localhost
set PORT=5432
set USER=postgres
set OLD_DB=apostapro_db
set NEW_DB=apostapro_utf8
set BACKUP_FILE=backup_apostapro_latin1.sql

:: Verificar se o pg_dump esta disponivel
if not exist "%PG_BIN%\pg_dump.exe" (
    echo [ERRO] PostgreSQL nao encontrado em: %PG_BIN%
    echo [INFO] Verifique se o PostgreSQL esta instalado corretamente.
    pause
    exit /b 1
)

:: Adicionar pasta do PostgreSQL ao PATH temporariamente
set "PATH=%PG_BIN%;%PATH%"

:: Verificar se o banco de dados de origem existe
echo Verificando banco de dados de origem: %OLD_DB%
"%PG_BIN%\psql.exe" -h %HOST% -p %PORT% -U %USER% -lqt | findstr /C:"%OLD_DB%" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] O banco de dados '%OLD_DB%' nao foi encontrado!
    echo [INFO] Verifique o nome do banco de dados de origem.
    pause
    exit /b 1
)

:: Exportar dados do banco antigo
echo.
echo [1/3] Exportando dados de %OLD_DB% para %BACKUP_FILE%...
"%PG_BIN%\pg_dump.exe" -h %HOST% -p %PORT% -U %USER% -d %OLD_DB% -F p -E LATIN1 -f "%BACKUP_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha na exportacao do banco de dados.
    echo [INFO] Verifique as credenciais e permissoes do usuario %USER%.
    pause
    exit /b 1
)

if not exist "%BACKUP_FILE%" (
    echo [ERRO] O arquivo de backup nao foi criado corretamente.
    pause
    exit /b 1
)

echo [OK] Exportacao concluida com sucesso! Tamanho: %%~zBACKUP_FILE% bytes
echo.

:: Verificar se o banco de destino existe
echo [2/3] Verificando banco de destino: %NEW_DB%
"%PG_BIN%\psql.exe" -h %HOST% -p %PORT% -U %USER% -lqt | findstr /C:"%NEW_DB%" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] O banco de dados '%NEW_DB%' nao foi encontrado!
    echo [INFO] Execute o script 'criar_banco_utf8.sql' primeiro.
    pause
    exit /b 1
)

:: Importar para o novo banco
echo [3/3] Importando dados para %NEW_DB%...
"%PG_BIN%\psql.exe" -h %HOST% -p %PORT% -U %USER% -d %NEW_DB% -f "%BACKUP_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha na importacao para o novo banco.
    echo [INFO] Verifique se ha espaco suficiente em disco e permissoes adequadas.
    pause
    exit /b 1
)

echo [OK] Importacao concluida com sucesso!
echo.

:: Verificar o novo banco
echo Tabelas no banco %NEW_DB%:
"%PG_BIN%\psql.exe" -h %HOST% -p %PORT% -U %USER% -d %NEW_DB% -c "\dt"

echo.
echo ===================================================
echo PROCESSO CONCLUIDO COM SUCESSO!
echo 1. Dados exportados para: %CD%\%BACKUP_FILE%
echo 2. Dados importados para: %NEW_DB%
echo.
echo [IMPORTANTE] Atualize a configuracao da aplicacao para usar o novo banco:
echo DATABASE_URL = "postgresql+psycopg2://postgres:Canjica@@2025@localhost:5432/apostapro_utf8"
echo ===================================================

:: Limpar variavel de senha
set PGPASSWORD=

pause
