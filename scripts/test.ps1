param(
    [string]$Database = "stockflow_test",
    [string]$Tags = "stockflow_core,stockflow_warehouse,stockflow_operations,stockflow_reports",
    [string]$Modules = "stockflow_core,stockflow_warehouse,stockflow_operations,stockflow_reports"
)

$ErrorActionPreference = "Stop"
docker compose exec odoo odoo -d $Database -i $Modules --test-enable --test-tags $Tags --stop-after-init --without-demo
