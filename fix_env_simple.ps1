# Script PowerShell simples para criar o arquivo .env
$envContent = "# PostgreSQL Configuration`r`n"
$envContent += "DB_HOST=localhost`r`n"
$envContent += "DB_PORT=5432`r`n"
$envContent += "DB_NAME=apostapro_db`r`n"
$envContent += "DB_USER=apostapro_user`r`n"
$envContent += "DB_PASSWORD=senha_segura_123`r`n`r`n"
$envContent += "# PostgreSQL Admin Configuration`r`n"
$envContent += "DB_ROOT_USER=postgres`r`n"
$envContent += "DB_ROOT_PASSWORD=postgres`r`n`r`n"
$envContent += "# Application Settings`r`n"
$envContent += "DEBUG=True`r`n"
$envContent += "ENVIRONMENT=development`r`n"
$envContent += "SECRET_KEY=change-this-in-production`r`n"
$envContent += "ALGORITHM=HS256`r`n"
$envContent += "ACCESS_TOKEN_EXPIRE_MINUTES=30`r`n`r`n"
$envContent += "# API Settings`r`n"
$envContent += "API_RELOAD=True`r`n"
$envContent += "API_HOST=0.0.0.0`r`n"
$envContent += "API_PORT=8000`r`n`r`n"
$envContent += "# FBRef Settings`r`n"
$envContent += "FBREF_BASE_URL=https://fbref.com`r`n`r`n"
$envContent += "# API Rate Limiting`r`n"
$envContent += "API_RATE_LIMIT=1000`r`n"
$envContent += "API_RATE_LIMIT_PERIOD=60`r`n"

# Fazer backup do arquivo .env atual se existir
if (Test-Path .env) {
    $backupPath = ".env.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item -Path .env -Destination $backupPath -Force
    Write-Host "Backup do arquivo .env criado como $backupPath"
}

# Escrever o novo conteúdo no arquivo .env
[System.IO.File]::WriteAllText("$PWD\.env", $envContent, [System.Text.Encoding]::UTF8)

Write-Host "Arquivo .env criado/atualizado com sucesso!"
