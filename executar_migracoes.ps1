# Script para executar migrações do Alembic
# Execute como Administrador

# Configurações
$env:DB_PASSWORD = "Canjica@@2025"
$env:DB_USER = "apostapro_user"
$env:DB_NAME = "apostapro_db"

# Ativar ambiente virtual (se existir)
$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
    .\venv\Scripts\Activate.ps1
}

# Instalar dependências se necessário
if (-not (Get-Command alembic -ErrorAction SilentlyContinue)) {
    Write-Host "Instalando dependências..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

# Verificar se o Alembic está instalado
if (-not (Get-Command alembic -ErrorAction SilentlyContinue)) {
    Write-Host "Erro: Alembic não encontrado. Instale com 'pip install alembic'" -ForegroundColor Red
    exit 1
}

# Executar migrações
Write-Host "`n🔧 Executando migrações do Alembic..." -ForegroundColor Cyan
# Verificar migrações pendentes
Write-Host "`n🔍 Verificando migrações pendentes..." -ForegroundColor Cyan
alembic current

# Executar upgrade para o head
Write-Host "`n🔄 Aplicando migrações..." -ForegroundColor Cyan
alembic upgrade head

# Verificar status
Write-Host "`n✅ Migrações concluídas com sucesso!" -ForegroundColor Green
Write-Host "`n📊 Status atual do banco de dados:" -ForegroundColor Cyan
alembic current

# Verificar tabelas criadas
Write-Host "`n📋 Tabelas no banco de dados:" -ForegroundColor Cyan
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U $env:DB_USER -d $env:DB_NAME -c "\dt"

# Manter o console aberto
Write-Host "`nPressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
