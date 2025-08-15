# Script PowerShell para criar o arquivo .env corretamente

# Conteúdo do arquivo .env
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

# Criar backup do arquivo .env atual se existir
if (Test-Path .env) {
    $backupName = ".env.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item -Path .env -Destination $backupName -Force
    Write-Host "✅ Backup do arquivo .env criado como $backupName"
}

# Criar o novo arquivo .env
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllLines("$PWD\.env", $envContent, $utf8NoBom)

# Verificar se o arquivo foi criado corretamente
if (Test-Path .env) {
    $fileContent = [System.IO.File]::ReadAllText("$PWD\.env", [System.Text.Encoding]::UTF8)
    
    if ($fileContent -eq $envContent) {
        Write-Host "✅ Arquivo .env criado com sucesso!"
        Write-Host "`n📝 Conteúdo do arquivo .env:"
        Write-Host ("-" * 50)
        Write-Host $fileContent.Trim()
        Write-Host ("-" * 50)
        exit 0
    } else {
        Write-Host "❌ Erro: O conteúdo salvo não corresponde ao conteúdo esperado."
        Write-Host "Tamanho esperado: $($envContent.Length), Tamanho salvo: $($fileContent.Length)"
        exit 1
    }
} else {
    Write-Host "❌ Erro: Falha ao criar o arquivo .env"
    exit 1
}
