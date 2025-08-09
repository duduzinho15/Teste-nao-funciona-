# Script para redefinir a senha do PostgreSQL
# Execute como Administrador

$ErrorActionPreference = "Stop"

try {
    # Parar o serviço do PostgreSQL
    Write-Host "Parando o serviço PostgreSQL..." -ForegroundColor Cyan
    Stop-Service postgresql-x64-17 -Force
    
    # Iniciar o PostgreSQL em modo single-user
    Write-Host "Iniciando PostgreSQL em modo single-user na porta 5433..." -ForegroundColor Cyan
    & "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" start -D "C:\Program Files\PostgreSQL\17\data" -w -t 60 -o "-p 5433" -s
    
    # Peça a nova senha de forma segura
    $newPassword = "Canjica@@2025"
    
    # Redefinir a senha
    Write-Host "Redefinindo a senha do usuário postgres..." -ForegroundColor Cyan
    & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -p 5433 -U postgres -c "ALTER USER postgres WITH PASSWORD '$newPassword';"
    
    # Parar o serviço
    Write-Host "Parando o PostgreSQL..." -ForegroundColor Cyan
    & "C:\Program Files\PostgreSQL\17\bin\pg_ctl.exe" stop -D "C:\Program Files\PostgreSQL\17\data" -m fast
    
    # Iniciar o serviço normalmente
    Write-Host "Iniciando o serviço PostgreSQL..." -ForegroundColor Cyan
    Start-Service postgresql-x64-17
    
    Write-Host "`n✅ Senha redefinida com sucesso para: $newPassword" -ForegroundColor Green
    Write-Host "Serviço PostgreSQL reiniciado com sucesso!" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Erro: $_" -ForegroundColor Red
    exit 1
}

# Manter o console aberto
Write-Host "`nPressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
