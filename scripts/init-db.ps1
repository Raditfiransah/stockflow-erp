param(
    [string]$Database = "stockflow",
    [string]$Modules = "stockflow_core,stockflow_warehouse,stockflow_operations,stockflow_reports"
)

$ErrorActionPreference = "Stop"
docker compose exec odoo odoo -d $Database -i $Modules --stop-after-init --without-demo
