# Script para verificar o status do serviço PostgreSQL

try {
    # Verifica se o serviço PostgreSQL está instalado
    $service = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue

    if ($service) {
        Write-Host "✅ Serviço PostgreSQL encontrado:" -ForegroundColor Green
        $service | Format-Table Name, DisplayName, Status -AutoSize
        
        # Verifica se o serviço está rodando
        if ($service.Status -eq 'Running') {
            Write-Host "✅ O serviço PostgreSQL está em execução." -ForegroundColor Green
            
            # Tenta obter a porta em que o PostgreSQL está escutando
            try {
                $port = (Get-NetTCPConnection -LocalPort 5432 -ErrorAction SilentlyContinue).LocalPort
                if ($port) {
                    Write-Host "✅ PostgreSQL está escutando na porta $port" -ForegroundColor Green
                } else {
                    Write-Host "⚠️  PostgreSQL não está escutando na porta 5432" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "⚠️  Não foi possível verificar a porta do PostgreSQL: $_" -ForegroundColor Yellow
            }
        } else {
            Write-Host "⚠️  O serviço PostgreSQL NÃO está em execução." -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Nenhum serviço PostgreSQL encontrado." -ForegroundColor Red
    }

    # Verifica se o PostgreSQL está no PATH
    $psqlPath = (Get-Command "psql" -ErrorAction SilentlyContinue).Source
    if ($psqlPath) {
        Write-Host "`n✅ psql encontrado em: $psqlPath" -ForegroundColor Green
        
        # Tenta obter a versão do PostgreSQL
        try {
            $version = & psql --version
            Write-Host "✅ $version" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Não foi possível obter a versão do psql: $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "`n❌ psql não encontrado no PATH." -ForegroundColor Red
        Write-Host "   Certifique-se de que o diretório bin do PostgreSQL está no PATH do sistema." -ForegroundColor Yellow
    }

    # Verifica variáveis de ambiente do PostgreSQL
    Write-Host "`n🔍 Variáveis de ambiente do PostgreSQL:" -ForegroundColor Cyan
    $pgVars = @('PGDATA', 'PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE')
    $foundVars = $false

    foreach ($var in $pgVars) {
        $value = [System.Environment]::GetEnvironmentVariable($var)
        if ($value) {
            Write-Host "✅ $var = $value" -ForegroundColor Green
            $foundVars = $true
        }
    }

    if (-not $foundVars) {
        Write-Host "ℹ️  Nenhuma variável de ambiente do PostgreSQL encontrada." -ForegroundColor Yellow
    }

    # Verifica se o PostgreSQL está acessível
    Write-Host "`n🔍 Testando conexão com o PostgreSQL..." -ForegroundColor Cyan

    # Tenta conectar usando psql se estiver disponível
    if ($psqlPath) {
        $result = & psql -U postgres -c "SELECT version();" -t 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Conexão bem-sucedida!" -ForegroundColor Green
            Write-Host "   $($result | Out-String)" -ForegroundColor Green
        } else {
            Write-Host "❌ Falha na conexão com psql:" -ForegroundColor Red
            Write-Host $result -ForegroundColor Red
        }
    } else {
        Write-Host "ℹ️  psql não encontrado, pulando teste de conexão." -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erro inesperado: $_" -ForegroundColor Red
    Write-Host "Detalhes: $($_.ScriptStackTrace)" -ForegroundColor Red
}

Write-Host "`n✅ Verificação concluída. Pressione qualquer tecla para sair..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
