# Setup MakerGit local PostgreSQL database on Windows

$DB_NAME = 'makergit'
$DB_USER = 'postgres'
$DB_PASSWORD = 'NatEvan12!!'
$DB_HOST = 'localhost'
$DB_PORT = '5432'
$SCHEMA_FILE = Join-Path $PSScriptRoot 'db\schema.sql'
$MIGRATION_FILE = Join-Path $PSScriptRoot 'db\migration.sql'

$psqlCmd = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlCmd) {
    $possiblePaths = @(
        "$env:ProgramFiles\PostgreSQL\16\bin",
        "$env:ProgramFiles\PostgreSQL\15\bin",
        "$env:ProgramFiles\PostgreSQL\14\bin",
        "$env:ProgramFiles\PostgreSQL\13\bin",
        "$env:ProgramFiles(x86)\PostgreSQL\16\bin",
        "$env:ProgramFiles(x86)\PostgreSQL\15\bin"
    ) | Where-Object { Test-Path $_ }

    if ($possiblePaths) {
        $psqlDir = $possiblePaths[0]
        $env:PATH = "$psqlDir;$env:PATH"
        $psqlCmd = Get-Command psql -ErrorAction SilentlyContinue
        Write-Host "Found psql in $psqlDir and added it to PATH."
    }
}

if (-not $psqlCmd) {
    Write-Error 'psql is not installed or not on PATH. Install PostgreSQL client tools first.'
    exit 1
}

$env:PGPASSWORD = $DB_PASSWORD
try {
    Write-Host "Checking if database '$DB_NAME' exists..."
    $dbExists = $false
    try {
        & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | Select-String -Pattern "^\s*$DB_NAME\s+" | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $dbExists = $true
        }
    } catch {
        # Database doesn't exist or can't connect
    }

    if (-not $dbExists) {
        Write-Host "Creating database '$DB_NAME'..."
        & createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
        if ($LASTEXITCODE -ne 0) {
            throw 'Failed to create database.'
        }

        Write-Host "Applying initial schema from $SCHEMA_FILE..."
        & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $SCHEMA_FILE
        if ($LASTEXITCODE -ne 0) {
            throw 'Failed to apply schema.'
        }
    } else {
        Write-Host "Database '$DB_NAME' already exists. Applying migration..."
        & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $MIGRATION_FILE
        if ($LASTEXITCODE -ne 0) {
            throw 'Failed to apply migration.'
        }
    }

    Write-Host 'Setup complete. Connector string:'
    Write-Host "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
} finally {
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}
