# Script para ativar o ambiente virtual do projeto ApostaPro
Write-Host "Ativando ambiente virtual do ApostaPro..." -ForegroundColor Green

# Verificar se o ambiente virtual existe
if (Test-Path "venv\Scripts\activate") {
    # Ativar o ambiente virtual
    & "venv\Scripts\activate"
    
    # Verificar se foi ativado corretamente
    if ($env:VIRTUAL_ENV) {
        Write-Host "Ambiente virtual ativado com sucesso!" -ForegroundColor Green
        Write-Host "Caminho: $env:VIRTUAL_ENV" -ForegroundColor Cyan
        Write-Host "Python: $(python --version)" -ForegroundColor Cyan
        
        # Verificar dependências principais
        Write-Host "Verificando dependências principais..." -ForegroundColor Yellow
        python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
        python -c "import alembic; print('Alembic:', alembic.__version__)"
        
    } else {
        Write-Host "Falha ao ativar o ambiente virtual" -ForegroundColor Red
    }
} else {
    Write-Host "Ambiente virtual nao encontrado em 'venv'" -ForegroundColor Red
    Write-Host "Execute: python -m venv venv" -ForegroundColor Yellow
}
