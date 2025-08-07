<#
.SYNOPSIS
    Script de diagnóstico para PostgreSQL no Windows
.DESCRIPTION
    Verifica o status do serviço PostgreSQL, configurações de autenticação,
    codificação do banco de dados e tenta conectar ao banco apostapro.
#>

# Configurações
$pgVersion = "17"  # Altere para a versão correta do PostgreSQL
$pgUser = "postgres"
$pgPassword = "@Eduardo123"
$pgHost = "localhost"
$pgPort = "5432"
$pgDatabase = "apostapro"

# Configura o encoding de saída para UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# Função para exibir mensagem de status
function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    
    $timeStamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = "White"
    $symbol = ""
    
    switch ($Status.ToUpper()) {
        "SUCCESS" { $color = "Green"; $symbol = "[+]" }
        "WARNING" { $color = "Yellow"; $symbol = "[!]" }
        "ERROR" { $color = "Red"; $symbol = "[X]" }
        default { $color = "Cyan"; $symbol = "[i]" }
    }
    
    Write-Host "[$timeStamp] [$symbol] " -NoNewline
    Write-Host $Message -ForegroundColor $color
}

# Função para executar comando SQL
function Invoke-PostgresSQL {
    param(
        [string]$sql,
        [string]$db = "postgres"
    )
    
    try {
        # Configura a senha como variável de ambiente apenas para este comando
        $env:PGPASSWORD = $pgPassword
        
        # Constrói o comando psql
        $psqlPath = "C:\\Program Files\\PostgreSQL\\$pgVersion\\bin\\psql.exe"
        $arguments = @(
            "-h", $pgHost,
            "-p", $pgPort,
            "-U", $pgUser,
            "-d", $db,
            "-c", $sql,
            "-A", "-t", "-F\t"
        )
        
        # Executa o comando e captura a saída
        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = $psqlPath
        $processInfo.RedirectStandardError = $true
        $processInfo.RedirectStandardOutput = $true
        $processInfo.UseShellExecute = $false
        $processInfo.Arguments = $arguments
        $processInfo.CreateNoWindow = $true
        
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $processInfo
        $process.Start() | Out-Null
        
        $output = $process.StandardOutput.ReadToEnd()
        $errorOutput = $process.StandardError.ReadToEnd()
        
        $process.WaitForExit()
        
        # Verifica se houve erro
        if ($process.ExitCode -ne 0 -or $errorOutput) {
            Write-Status "Erro ao executar comando SQL: $errorOutput" -Status "ERROR"
            return $null
        }
        
        return $output.Trim()
    }
    catch {
        Write-Status "Exceção ao executar comando SQL: $_" -Status "ERROR"
        return $null
    }
    finally {
        # Remove a senha da memória
        Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
    }
}

# Início do diagnóstico
Write-Host "`n"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DIAGNÓSTICO POSTGRESQL - APOSTAPRO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Cyan

# 1. Verifica se o serviço PostgreSQL está rodando
try {
    $service = Get-Service -Name "postgresql-x64-$pgVersion*" -ErrorAction Stop
    Write-Status "Serviço PostgreSQL: $($service.Status)" -Status "SUCCESS"
    
    if ($service.Status -ne "Running") {
        Write-Status "Iniciando o serviço PostgreSQL..." -Status "WARNING"
        Start-Service -Name $service.Name -ErrorAction Stop
        Start-Sleep -Seconds 2
        $service.Refresh()
        Write-Status "Status após tentativa de início: $($service.Status)" -Status "INFO"
    }
}
catch {
    Write-Status "Erro ao verificar/iniciar o serviço PostgreSQL: $_" -Status "ERROR"
    exit 1
}

# 2. Verifica conexão com o banco de dados
Write-Host "`n[1/4] Verificando conexão com o PostgreSQL..." -ForegroundColor Yellow
$testConn = Invoke-PostgresSQL -sql "SELECT version();"

if ($testConn) {
    Write-Status "Conexão bem-sucedida!" -Status "SUCCESS"
    Write-Host "   $testConn" -ForegroundColor Gray
} else {
    Write-Status "Falha ao conectar ao PostgreSQL" -Status "ERROR"
    Write-Host "`nVerifique se:" -ForegroundColor Red
    Write-Host "1. O serviço PostgreSQL está rodando" -ForegroundColor Red
    Write-Host "2. O usuário e senha estão corretos" -ForegroundColor Red
    Write-Host "3. O arquivo pg_hba.conf permite conexões locais" -ForegroundColor Red
    exit 1
}

# 3. Verifica configurações de codificação
Write-Host "`n[2/4] Verificando configurações de codificação..." -ForegroundColor Yellow

# Verifica encoding do banco postgres
$dbInfo = Invoke-PostgresSQL -sql "SELECT current_database(), pg_encoding_to_char(encoding), datcollate, datctype FROM pg_database WHERE datname = current_database();"
if ($dbInfo) {
    $dbName, $dbEncoding, $dbCollate, $dbCtype = $dbInfo -split "\t"
    Write-Status "Banco de dados: $dbName" -Status "INFO"
    Write-Status "Codificação: $dbEncoding" -Status "INFO"
    Write-Status "Collation: $dbCollate" -Status "INFO"
    Write-Status "CType: $dbCtype" -Status "INFO"
    
    if ($dbEncoding -ne "UTF8") {
        Write-Status "AVISO: A codificação não é UTF-8. Isso pode causar problemas com caracteres especiais." -Status "WARNING"
    }
}

# 4. Verifica se o banco apostapro existe
Write-Host "`n[3/4] Verificando banco de dados 'apostapro'..." -ForegroundColor Yellow
$dbExists = Invoke-PostgresSQL -sql "SELECT 1 FROM pg_database WHERE datname = '$pgDatabase';"

if ($dbExists) {
    Write-Status "O banco de dados '$pgDatabase' existe." -Status "SUCCESS"
    
    # Verifica encoding do banco apostapro
    $apostaproInfo = Invoke-PostgresSQL -sql "SELECT pg_encoding_to_char(encoding), datcollate, datctype FROM pg_database WHERE datname = '$pgDatabase';" -db $pgDatabase
    if ($apostaproInfo) {
        $apostaproEncoding, $apostaproCollate, $apostaproCtype = $apostaproInfo -split "\t"
        Write-Status "Codificação: $apostaproEncoding" -Status "INFO"
        Write-Status "Collation: $apostaproCollate" -Status "INFO"
        Write-Status "CType: $apostaproCtype" -Status "INFO"
    }
    
    # Lista tabelas no banco apostapro
    $tables = Invoke-PostgresSQL -sql "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" -db $pgDatabase
    if ($tables) {
        Write-Status "Tabelas encontradas ($($tables.Count)):" -Status "SUCCESS"
        $tables | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }
    } else {
        Write-Status "Nenhuma tabela encontrada no banco '$pgDatabase'." -Status "WARNING"
    }
} else {
    Write-Status "O banco de dados '$pgDatabase' não existe." -Status "WARNING"
}

# 5. Verifica configurações do servidor
Write-Host "`n[4/4] Verificando configurações do servidor..." -ForegroundColor Yellow

# Configurações de locale
$lcSettings = @(
    "lc_messages", "lc_monetary", "lc_numeric", "lc_time"
)

foreach ($setting in $lcSettings) {
    $value = Invoke-PostgresSQL -sql "SHOW $setting;"
    Write-Status "$setting`: $value" -Status "INFO"
}

# Configurações de autenticação
Write-Host "`nVerificando configurações de autenticação..." -ForegroundColor Yellow
$hbaPath = "C:\\Program Files\\PostgreSQL\\$pgVersion\\data\\pg_hba.conf"
if (Test-Path $hbaPath) {
    try {
        $hbaContent = Get-Content $hbaPath -Raw -ErrorAction Stop
        
        # Extrai regras IPv4
        $ipv4Rules = $hbaContent -split "`n" | 
            Where-Object { $_ -match '^\s*[^#]' -and $_ -match '127\.0\.0\.1/32' }
        
        if ($ipv4Rules) {
            Write-Status "Regras IPv4 locais encontradas:" -Status "INFO"
            $ipv4Rules | ForEach-Object { 
                $rule = $_.Trim() -replace '\s+', ' '  # Normaliza espaços
                Write-Host "   $rule" -ForegroundColor Gray 
            }
        } else {
            Write-Status "Nenhuma regra IPv4 local encontrada no pg_hba.conf" -Status "WARNING"
        }
        
        # Verifica regras locais (unix socket)
        $localRules = $hbaContent -split "`n" | 
            Where-Object { $_ -match '^\s*local\s+all' }
            
        if ($localRules) {
            Write-Status "Regras de conexão local (socket):" -Status "INFO"
            $localRules | ForEach-Object { 
                $rule = $_.Trim() -replace '\s+', ' '  # Normaliza espaços
                Write-Host "   $rule" -ForegroundColor Gray 
            }
        } else {
            Write-Status "AVISO: Não há regras para conexões locais via socket no pg_hba.conf" -Status "WARNING"
        }
    }
    catch {
        Write-Status "Erro ao ler o arquivo pg_hba.conf: $_" -Status "ERROR"
    }
} else {
    Write-Status "Não foi possível encontrar o arquivo pg_hba.conf em $hbaPath" -Status "ERROR"
}

# Resumo final
Write-Host "`n"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMO DO DIAGNÓSTICO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($testConn) {
    Write-Status "✅ Conexão com o PostgreSQL bem-sucedida" -Status "SUCCESS"
} else {
    Write-Status "❌ Falha na conexão com o PostgreSQL" -Status "ERROR"
}

if ($dbExists) {
    Write-Status "✅ Banco de dados '$pgDatabase' encontrado" -Status "SUCCESS"
    if ($apostaproEncoding -and $apostaproEncoding -ne "UTF8") {
        Write-Status "⚠️  AVISO: O banco está usando codificação $apostaproEncoding (recomendado: UTF8)" -Status "WARNING"
    }
} else {
    Write-Status "⚠️  Banco de dados '$pgDatabase' não encontrado" -Status "WARNING"
}

if ($tables) {
    Write-Status "✅ Foram encontradas $($tables.Count) tabelas no banco '$pgDatabase'" -Status "SUCCESS"
} elseif ($dbExists) {
    Write-Status "⚠️  Nenhuma tabela encontrada no banco '$pgDatabase'" -Status "WARNING"
}

Write-Host "`nPróximos passos recomendados:" -ForegroundColor Yellow
if (-not $testConn) {
    Write-Host "1. Verifique se o serviço PostgreSQL está rodando" -ForegroundColor White
    Write-Host "2. Confirme o usuário e senha em database/config.py" -ForegroundColor White
    Write-Host "3. Verifique as configurações em pg_hba.conf" -ForegroundColor White
}
elseif (-not $dbExists) {
    Write-Host "1. Crie o banco de dados 'apostapro' com a codificação UTF-8" -ForegroundColor White
    Write-Host "   Exemplo: CREATE DATABASE apostapro WITH ENCODING 'UTF8' LC_COLLATE 'pt_BR.UTF-8' LC_CTYPE 'pt_BR.UTF-8' TEMPLATE template0;" -ForegroundColor Gray
}
elseif (-not $tables) {
    Write-Host "1. Execute as migrações do Alembic para criar as tabelas" -ForegroundColor White
    Write-Host "   > cd database && alembic upgrade head" -ForegroundColor Gray
}
else {
    Write-Host "✅ O banco de dados parece estar configurado corretamente." -ForegroundColor Green
    Write-Host "   Você pode prosseguir com os testes de integração." -ForegroundColor Green
}

Write-Host "`nPressione Enter para sair..." -NoNewline
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
