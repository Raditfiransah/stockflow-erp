param(
    [Parameter(Mandatory = $true)][string]$Dump,
    [string]$Database = "stockflow"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $Dump)) {
    throw "Dump file not found: $Dump"
}
docker compose exec -T db dropdb -U odoo --if-exists $Database
docker compose exec -T db createdb -U odoo $Database
Get-Content -Raw -LiteralPath $Dump | docker compose exec -T db pg_restore -U odoo -d $Database --no-owner
Write-Output "Restored $Dump into $Database"
