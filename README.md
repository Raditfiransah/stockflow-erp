# StockFlow ERP

Inventory and warehouse management for **PT StockFlow Distribusi**, built on Odoo 20 Community Edition.

## Stack

| Layer | Choice |
|---|---|
| ERP | Odoo 20 Community (`odoo:20.0`) |
| Database | PostgreSQL 16 |
| Runtime | Docker Compose |
| Custom code | Python / Odoo ORM, QWeb |

## Quick start

```powershell
Copy-Item .env.example .env
docker compose up -d
docker compose exec odoo odoo -d stockflow -i stockflow_core,stockflow_warehouse,stockflow_operations,stockflow_reports --stop-after-init --without-demo
```

Open <http://localhost:8070> and log in with the database `stockflow`.

Optional UAT data (3 warehouses, 12 products, 10 partners):

```powershell
docker compose exec odoo odoo -d stockflow -i stockflow_demo --stop-after-init --without-demo
```

## Modules

| Module | Depends on | What it adds |
|---|---|---|
| `stockflow_core` | `base`, `product`, `stock` | SKU policy (normalised, unique, required for storable goods), partner code, product categories, StockFlow settings |
| `stockflow_warehouse` | `stock`, `stockflow_core` | Negative-stock guard, internal-transfer approval, stock movement types, movement ledger |
| `stockflow_operations` | `purchase`, `purchase_stock`, `sale`, `sale_stock` | Receipt requires a confirmed PO, delivery requires a confirmed SO, partner purchase/sales history |
| `stockflow_reports` | `stockflow_operations`, `stockflow_warehouse` | Inventory, sales and purchasing report wizards with PDF output |
| `stockflow_demo` | `stockflow_reports` | Sample warehouses, products and partners (`noupdate`, never installed by default) |

## Menus

- **Inventory → Reporting → Stock Movement Ledger** — every stock move with type, product, locations, partner, state.
- **Inventory → Reporting → StockFlow Reports** — inventory, sales and purchasing PDF reports.
- **Inventory → Configuration → Products → Products Without SKU** — audit list.
- **Settings → StockFlow** — business rule toggles.
- **Contacts → any partner → StockFlow tab / smart buttons** — partner code, purchase and sales history.

## Business rules enforced

1. Every storable product has a SKU; SKUs are unique and stored uppercase.
2. Internal and transit locations cannot hold a negative quantity.
3. Every stock move is recorded with a movement type, source, destination, document reference and timestamp.
4. Internal transfers need approval before validation and must use two different locations with positive quantities.
5. Receipts must reference a confirmed purchase order.
6. Deliveries must reference a confirmed sales order.
7. Returns (`return_id`) are exempt from rules 5 and 6.
8. Documents keep an activity history through Odoo's chatter.

All rules are switchable in **Settings → StockFlow**.

## Testing

```powershell
.\scripts\test.ps1
```

or directly:

```powershell
docker compose exec odoo odoo -d stockflow_test -i stockflow_core,stockflow_warehouse,stockflow_operations,stockflow_reports --test-enable --test-tags stockflow_core,stockflow_warehouse,stockflow_operations,stockflow_reports --stop-after-init --without-demo
```

22 tests cover SKU policy, the negative-stock guard, internal transfer approval, purchase and sales flows, and report output.

## Operations

```powershell
.\scripts\init-db.ps1      # install modules into stockflow
.\scripts\backup.ps1       # pg_dump + filestore archive into backups/
.\scripts\restore.ps1 -Dump backups\stockflow-<stamp>.dump
```

## Configuration

`.env` (never committed):

| Variable | Default | Purpose |
|---|---|---|
| `POSTGRES_USER` | `odoo` | Database user |
| `POSTGRES_PASSWORD` | `odoo` | Database password |
| `ODOO_PORT` | `8070` | Host port for the web UI |
| `ODOO_LONGPOLLING_PORT` | `8072` | Host port for longpolling |
| `ODOO_MASTER_PASSWORD` | `admin` | Master password for the web database manager |

Change the database password before any shared deployment, and change the Odoo `admin` password on first login.

### Master password

The **master password** is what the web database manager asks for when you create, duplicate, back up, restore or delete a database. It is unrelated to the `admin` login user.

- It comes from `ODOO_MASTER_PASSWORD` in `.env`, rendered into the container's `odoo.conf` on start.
- Default is `admin`. Odoo flags that as unprotected and shows a banner offering to set a real one; setting a different value in `.env` removes the banner.
- Changing it in the UI (**Set Master Password**) sticks across `docker compose restart`, because the rendered file is writable.
- Recreating the container (`docker compose up -d --force-recreate`, or any change to the `odoo` service) re-renders from `.env`, so **`.env` wins**.
- Forgot it? Set `ODOO_MASTER_PASSWORD` in `.env` and recreate the container.

`Database management function blocked, bad admin password` means the password you typed did not match. It is not a system fault.

### Creating a second database

`db_name` is intentionally not pinned in `odoo.conf`, so the manager lists every database. The root URL still opens `stockflow` while it is the only database. For scripted setups use `scripts/init-db.ps1 -Database <name>`.

Before exposing this stack beyond your machine, set `list_db = False` in `config/odoo.conf.template` to disable the web database manager entirely.


## Documentation

- `docs/architecture.md` — module design and Odoo 20 specifics
- `docs/business-rules.md` — rule-by-rule implementation
- `docs/brd-traceability.md` — BRD requirement to code mapping
- `docs/user-guide.md` — day-to-day procedures
- `docs/test-plan.md` — test inventory and UAT checklist
