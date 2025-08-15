# Script PowerShell para criar o arquivo .env corretamente
$envContent = @"
# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=apostapro_db
DB_USER=apostapro_user
DB_PASSWORD=senha_segura_123

# PostgreSQL Admin Configuration
DB_ROOT_USER=postgres
DB_ROOT_PASSWORD=postgres

# Application Settings
DEBUG=True
ENVIRONMENT=development
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_RELOAD=True
API_HOST=0.0.0.0
API_PORT=8000

# FBRef Settings
FBREF_BASE_URL=https://fbref.com

# API Rate Limiting
API_RATE_LIMIT=1000
API_RATE_LIMIT_PERIOD=60
"@

# Fazer backup do arquivo .env atual se existir
if (Test-Path .env) {
    $backupPath = ".env.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item -Path .env -Destination $backupPath -Force
    Write-Host "✅ Backup do arquivo .env criado como $backupPath"
}

# Escrever o novo conteúdo no arquivo .env
$envContent | Out-File -FilePath .env -Encoding utf8 -NoNewline

Write-Host "✅ Arquivo .env criado/atualizado com sucesso!"
Write-Host "`n📝 Conteúdo do arquivo .env:"
Write-Host ("-" * 50)
Get-Content .env | ForEach-Object { Write-Host $_ }
Write-Host ("-" * 50)
