param(
    [string]$Database = "stockflow",
    [string]$OutputDir = "backups"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
docker compose exec -T db pg_dump -U odoo -Fc $Database > (Join-Path $OutputDir "$Database-$stamp.dump")
docker compose exec -T odoo tar czf - -C /var/lib/odoo filestore > (Join-Path $OutputDir "$Database-$stamp-filestore.tar.gz")
Write-Output "Backup written to $OutputDir"
