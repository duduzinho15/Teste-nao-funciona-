# Script para configurar o banco de dados PostgreSQL
# Execute como Administrador

# Carregar variáveis de ambiente do arquivo .env
$envFile = ".\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "Arquivo .env não encontrado!" -ForegroundColor Red
    exit 1
}

# Carregar variáveis de ambiente
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Configurações
$dbName = $env:DB_NAME
$dbUser = $env:DB_USER
$dbPassword = $env:DB_PASSWORD
$pgBin = "C:\Program Files\PostgreSQL\17\bin"

# Função para executar comandos SQL
function Execute-SQL {
    param (
        [string]$sqlCommand,
        [string]$db = "postgres"
    )
    
    try {
        $env:PGPASSWORD = $dbPassword
        & "$pgBin\psql.exe" -h localhost -U postgres -d $db -c $sqlCommand
        if ($LASTEXITCODE -ne 0) {
            throw "Erro ao executar comando SQL"
        }
        return $true
    }
    catch {
        Write-Host "Erro ao executar comando SQL: $_" -ForegroundColor Red
        return $false
    }
}

# Verificar se o PostgreSQL está rodando
try {
    $service = Get-Service -Name postgresql-x64-17 -ErrorAction Stop
    if ($service.Status -ne "Running") {
        Write-Host "Iniciando o serviço PostgreSQL..." -ForegroundColor Yellow
        Start-Service -Name postgresql-x64-17 -ErrorAction Stop
    }
}
catch {
    Write-Host "Erro ao verificar/iniciar o serviço PostgreSQL: $_" -ForegroundColor Red
    exit 1
}

# 1. Criar usuário se não existir
Write-Host "Verificando/criando usuário $dbUser..." -ForegroundColor Cyan
$userExists = Execute-SQL "SELECT 1 FROM pg_roles WHERE rolname = '$dbUser'"
if (-not $userExists) {
    Write-Host "Criando usuário $dbUser..." -ForegroundColor Cyan
    $createUser = Execute-SQL "CREATE USER $dbUser WITH PASSWORD '$dbPassword';"
    if (-not $createUser) {
        Write-Host "Erro ao criar usuário $dbUser" -ForegroundColor Red
        exit 1
    }
}

# 2. Criar banco de dados se não existir
Write-Host "Verificando/criando banco de dados $dbName..." -ForegroundColor Cyan
$dbExists = Execute-SQL "SELECT 1 FROM pg_database WHERE datname = '$dbName'"
if (-not $dbExists) {
    Write-Host "Criando banco de dados $dbName..." -ForegroundColor Cyan
    $createDb = Execute-SQL "CREATE DATABASE $dbName WITH ENCODING = 'UTF8' LC_COLLATE = 'Portuguese_Brazil.1252' LC_CTYPE = 'Portuguese_Brazil.1252' TEMPLATE = template0;"
    if (-not $createDb) {
        Write-Host "Erro ao criar banco de dados $dbName" -ForegroundColor Red
        exit 1
    }
    
    # Conceder privilégios
    $grantPrivileges = Execute-SQL "GRANT ALL PRIVILEGES ON DATABASE $dbName TO $dbUser;" $dbName
    if (-not $grantPrivileges) {
        Write-Host "Erro ao conceder privilégios ao usuário $dbUser" -ForegroundColor Yellow
    }
}

# 3. Criar extensão se não existir
Write-Host "Verificando/criando extensão uuid-ossp..." -ForegroundColor Cyan
$extensionExists = Execute-SQL "SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp';" $dbName
if (-not $extensionExists) {
    $createExtension = Execute-SQL "CREATE EXTENSION IF NOT EXISTS ""uuid-ossp"";" $dbName
    if (-not $createExtension) {
        Write-Host "Aviso: Não foi possível criar a extensão uuid-ossp" -ForegroundColor Yellow
    }
}

# 4. Verificar se o usuário tem permissões
Write-Host "Verificando permissões do usuário $dbUser..." -ForegroundColor Cyan
$hasPrivileges = Execute-SQL "SELECT has_database_privilege('$dbUser', '$dbName', 'CONNECT');" $dbName
if ($hasPrivileges -notmatch "t") {
    Write-Host "Concedendo permissões ao usuário $dbUser..." -ForegroundColor Cyan
    $grantAll = Execute-SQL "GRANT ALL PRIVILEGES ON DATABASE $dbName TO $dbUser;"
    $grantAllSchema = Execute-SQL "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $dbUser;" $dbName
    $grantAllSequences = Execute-SQL "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $dbUser;" $dbName
    $grantAllFunctions = Execute-SQL "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $dbUser;" $dbName
    $alterDefault = Execute-SQL "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $dbUser;" $dbName
}

# 5. Verificar tabelas
Write-Host "Verificando tabelas no banco de dados $dbName..." -ForegroundColor Cyan
$tables = & "$pgBin\psql.exe" -h localhost -U postgres -d $dbName -t -c "\dt"
if ($tables) {
    Write-Host "Tabelas encontradas em $dbName :" -ForegroundColor Green
    $tables | ForEach-Object { Write-Host "- $_" }
} else {
    Write-Host "Nenhuma tabela encontrada em $dbName" -ForegroundColor Yellow
    Write-Host "Você precisa executar as migrações do Alembic para criar as tabelas." -ForegroundColor Yellow
}

# 6. Configuração final
Write-Host "`n✅ Configuração do banco de dados concluída com sucesso!" -ForegroundColor Green
Write-Host "`n📝 Resumo da configuração:" -ForegroundColor Cyan
Write-Host "- Banco de Dados: $dbName"
Write-Host "- Usuário: $dbUser"
Write-Host "- Host: localhost"
Write-Host "- Porta: 5432"

Write-Host "`n🔧 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Execute as migrações do Alembic para criar as tabelas"
Write-Host "2. Execute os scripts de coleta de dados para popular o banco"

# Limpar senha da memória
Remove-Variable -Name PGPASSWORD -ErrorAction SilentlyContinue
[System.GC]::Collect()

# Manter o console aberto
Write-Host "`nPressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
