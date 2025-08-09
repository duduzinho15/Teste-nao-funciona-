# Fix PostgreSQL Migrations Script
# This script will help diagnose and fix the migration issues

# Load environment variables from .env file
$envContent = Get-Content -Path "$PSScriptRoot\.env" -Raw
$envContent -split "`n" | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim('"\' ')
        [Environment]::SetEnvironmentVariable($key, $value)
    }
}

# Database connection parameters
$dbHost = [Environment]::GetEnvironmentVariable("DB_HOST", "Process") ?? "localhost"
$dbPort = [Environment]::GetEnvironmentVariable("DB_PORT", "Process") ?? "5432"
$dbName = [Environment]::GetEnvironmentVariable("DB_NAME", "Process") ?? "apostapro_db"
$dbUser = [Environment]::GetEnvironmentVariable("DB_USER", "Process") ?? "apostapro_user"
$dbPass = [Environment]::GetEnvironmentVariable("DB_PASSWORD", "Process") ?? "senha_segura_123"

# Connection string for psql
$env:PGPASSWORD = $dbPass

Write-Host "=== PostgreSQL Migration Fix Tool ===" -ForegroundColor Cyan
Write-Host "Database: $dbName@$dbHost:$dbPort as $dbUser"
Write-Host ""

# Function to execute SQL and return results
function Invoke-PostgresQuery {
    param (
        [string]$sql,
        [string]$database = $dbName
    )
    
    try {
        $result = & psql -h $dbHost -p $dbPort -U $dbUser -d $database -t -A -F"," -c $sql 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Error executing query: $sql" -ForegroundColor Red
            Write-Host $result -ForegroundColor Red
            return $null
        }
        return $result
    }
    catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
        return $null
    }
}

# Check PostgreSQL version
Write-Host "Checking PostgreSQL version..." -ForegroundColor Yellow
$version = Invoke-PostgresQuery -sql "SELECT version();" -database "postgres"
Write-Host "✅ $version" -ForegroundColor Green

# Check if database exists
Write-Host "`nChecking if database '$dbName' exists..." -ForegroundColor Yellow
$dbExists = Invoke-PostgresQuery -sql "SELECT 1 FROM pg_database WHERE datname = '$dbName';" -database "postgres"

if ([string]::IsNullOrEmpty($dbExists)) {
    Write-Host "❌ Database '$dbName' does not exist" -ForegroundColor Red
    $createDb = Read-Host "Do you want to create the database? (y/n)"
    if ($createDb -eq 'y') {
        Write-Host "Creating database '$dbName'..." -ForegroundColor Yellow
        $result = Invoke-PostgresQuery -sql "CREATE DATABASE $dbName;" -database "postgres"
        if ($result) {
            Write-Host "✅ Database created successfully" -ForegroundColor Green
        }
    } else {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✅ Database '$dbName' exists" -ForegroundColor Green
}

# Check if alembic_version table exists
Write-Host "`nChecking alembic_version table..." -ForegroundColor Yellow
$alembicTable = Invoke-PostgresQuery -sql "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'alembic_version';"

if ([string]::IsNullOrEmpty($alembicTable)) {
    Write-Host "❌ alembic_version table does not exist" -ForegroundColor Red
    $initAlembic = Read-Host "Do you want to initialize Alembic? (y/n)"
    if ($initAlembic -eq 'y') {
        Write-Host "Initializing Alembic..." -ForegroundColor Yellow
        & alembic init -t async migrations
        Write-Host "✅ Alembic initialized" -ForegroundColor Green
    }
} else {
    $currentVersion = Invoke-PostgresQuery -sql "SELECT version_num FROM alembic_version;"
    Write-Host "✅ alembic_version exists. Current version: $currentVersion" -ForegroundColor Green
}

# List all tables
Write-Host "`nListing all tables in '$dbName':" -ForegroundColor Yellow
$tables = Invoke-PostgresQuery -sql "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"

if ([string]::IsNullOrEmpty($tables)) {
    Write-Host "No tables found in the database" -ForegroundColor Yellow
} else {
    $tables -split "`n" | ForEach-Object { Write-Host "- $_" }
}

# Check if posts_redes_sociais table exists
Write-Host "`nChecking for 'posts_redes_sociais' table..." -ForegroundColor Yellow
$postsTable = Invoke-PostgresQuery -sql "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts_redes_sociais';"

if ([string]::IsNullOrEmpty($postsTable)) {
    Write-Host "❌ 'posts_redes_sociais' table does not exist" -ForegroundColor Red
    
    # Find the migration file for posts_redes_sociais
    $migrationFile = Get-ChildItem -Path "$PSScriptRoot\alembic\versions" -Filter "*posts_redes_sociais*.py" | Select-Object -First 1
    
    if ($null -ne $migrationFile) {
        Write-Host "Found migration file: $($migrationFile.Name)" -ForegroundColor Yellow
        $applyMigration = Read-Host "Do you want to apply this migration? (y/n)"
        
        if ($applyMigration -eq 'y') {
            Write-Host "Applying migration $($migrationFile.Name)..." -ForegroundColor Yellow
            & alembic upgrade head
            
            # Check if table was created
            $postsTable = Invoke-PostgresQuery -sql "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts_redes_sociais';"
            if (-not [string]::IsNullOrEmpty($postsTable)) {
                Write-Host "✅ 'posts_redes_sociais' table created successfully" -ForegroundColor Green
            } else {
                Write-Host "❌ Failed to create 'posts_redes_sociais' table" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "No migration file found for 'posts_redes_sociais'" -ForegroundColor Red
    }
} else {
    Write-Host "✅ 'posts_redes_sociais' table exists" -ForegroundColor Green
}

Write-Host "`n=== Script completed ===" -ForegroundColor Cyan
