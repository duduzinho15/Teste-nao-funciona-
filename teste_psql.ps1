# Script simples para testar conexão com PostgreSQL

# Configurações
$pgVersion = "17"
$pgUser = "postgres"
$pgPassword = "@Eduardo123"
$pgHost = "localhost"
$pgPort = "5432"
$pgDatabase = "postgres"

# Caminho para o executável psql
$psqlPath = "C:\Program Files\PostgreSQL\$pgVersion\bin\psql.exe"

# Verifica se o psql existe
if (-not (Test-Path $psqlPath)) {
    Write-Host "Erro: psql.exe não encontrado em $psqlPath" -ForegroundColor Red
    exit 1
}

# Define a senha como variável de ambiente
$env:PGPASSWORD = $pgPassword

# Comando para testar a conexão
$command = "& '$psqlPath' -h $pgHost -p $pgPort -U $pgUser -d $pgDatabase -c \"SELECT version();\""

Write-Host "Testando conexão com PostgreSQL..." -ForegroundColor Yellow
Write-Host "Comando: $command" -ForegroundColor Gray

try {
    # Executa o comando e captura a saída
    $output = Invoke-Expression $command 2>&1
    
    # Verifica se houve erro
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao conectar ao PostgreSQL:" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        
        # Verifica se o serviço está rodando
        $service = Get-Service -Name "postgresql-x64-$pgVersion*" -ErrorAction SilentlyContinue
        if ($service) {
            Write-Host "`nStatus do serviço PostgreSQL: $($service.Status)" -ForegroundColor Cyan
            if ($service.Status -ne "Running") {
                Write-Host "Tentando iniciar o serviço..." -ForegroundColor Yellow
                Start-Service -Name $service.Name -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
                $service.Refresh()
                Write-Host "Novo status: $($service.Status)" -ForegroundColor Cyan
            }
        } else {
            Write-Host "Serviço PostgreSQL não encontrado." -ForegroundColor Red
        }
        
        # Verifica a porta
        $portInUse = Test-NetConnection -ComputerName localhost -Port $pgPort -InformationLevel Quiet
        if ($portInUse) {
            Write-Host "A porta $pgPort está em uso." -ForegroundColor Green
        } else {
            Write-Host "A porta $pgPort não está respondendo." -ForegroundColor Red
        }
    } else {
        Write-Host "Conexão bem-sucedida!" -ForegroundColor Green
        Write-Host $output -ForegroundColor Green
        
        # Se a conexão foi bem-sucedida, verifica o banco apostapro
        $checkDb = "& '$psqlPath' -h $pgHost -p $pgPort -U $pgUser -d $pgDatabase -c \"SELECT datname, pg_encoding_to_char(encoding) FROM pg_database WHERE datname IN ('postgres', 'apostapro');\""
        Write-Host "`nVerificando bancos de dados..." -ForegroundColor Yellow
        $dbOutput = Invoke-Expression $checkDb 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host $dbOutput -ForegroundColor Green
        } else {
            Write-Host "Erro ao verificar bancos de dados:" -ForegroundColor Red
            Write-Host $dbOutput -ForegroundColor Red
        }
    }
}
catch {
    Write-Host "Erro ao executar o teste: $_" -ForegroundColor Red
}
finally {
    # Remove a senha da memória
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}

Write-Host "`nPressione Enter para sair..." -NoNewline
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
