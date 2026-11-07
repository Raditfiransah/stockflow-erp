# Architecture

## Module graph

```
stockflow_core          (master data, settings)
    └── stockflow_warehouse        (stock rules, transfers, traceability)
            └── stockflow_operations       (purchase / sales integration)
                    └── stockflow_reports  (PDF reports)
                            └── stockflow_demo  (sample data, optional)
```

Every module inherits standard Odoo models. No Odoo core file is modified, so the stack can be upgraded by pulling a newer `odoo:20.0` image.

## `stockflow_core`

| File | Purpose |
|---|---|
| `models/product.py` | SKU normalisation, uniqueness and "required for storable" rule |
| `models/res_partner.py` | `stockflow_code`, unique per company |
| `models/res_config_settings.py` | Four business-rule toggles |
| `models/stockflow_settings.py` | `stockflow.settings` abstract model with `stockflow_get_bool()` |
| `data/stockflow_config_data.xml` | Defaults the four parameters to `1` |
| `data/product_category_data.xml` | Five seed categories |

SKU handling lives in two places on purpose:

- `product.template` enforces "storable products need a SKU" and uniqueness after the template and its variants exist.
- `product.product` normalises and enforces uniqueness for direct variant edits.

`ProductProduct.create()` creates its template before applying variant fields, so it runs the template-level rule with `stockflow_skip_sku_check` and re-validates once the variant exists. Without that, creating a variant with a SKU would fail.

## `stockflow_warehouse`

**Negative stock.** `stock.quant._update_available_quantity()` is the single point every stock change passes through. After the write, the guard re-reads the quants for the exact product/location/lot/package/owner combination and raises `UserError` when the result is below zero. It only applies to `internal` and `transit` locations and only when `stockflow.block_negative_stock` is on. A `stockflow_allow_negative` context key bypasses it for migrations and system operations.

Raising after the write is safe because Odoo rolls back the transaction on `UserError`.

**Internal transfers.** Approval fields plus `_stockflow_check_internal_transfer()`, called from `button_validate()`. The check covers: same source and destination, empty move list, non-positive quantities, and missing approval. Standard Odoo states (`draft → waiting → confirmed → assigned → done`) are untouched; approval is an extra gate in front of validation.

**Traceability.** `stock.move.stockflow_movement_type` is a stored computed selection derived from `is_inventory`, `origin_returned_move_id` and the picking type. The ledger views read `stock.move` directly, so the data is the same one Odoo uses.

## `stockflow_operations`

`button_validate()` on `stock.picking` calls `_stockflow_check_source_document()`:

- `incoming` → every move must link to a `purchase.order` in `purchase` or `done`.
- `outgoing` → every move must link to a `sale.order` in `sale` or `done`.
- `return_id` set → skipped.
- Setting off → skipped.

Orders are read from the moves (`purchase_line_id.order_id`, `sale_line_id.order_id`) rather than the picking's related fields, so a picking with mixed or missing lines is rejected correctly.

## `stockflow_reports`

Three `TransientModel` wizards collect filters and expose `get_report_data()`. QWeb templates call that method, so the same logic feeds the PDF and any future export. Quantities come from `_read_group`, not from Python loops over records.

## Odoo 20 differences that shaped this code

These were verified against the running `odoo:20.0` image, not assumed:

| Topic | Odoo 20 behaviour | Consequence here |
|---|---|---|
| Access rights model | `ir.model.access` renamed to `ir.access`; CSV columns are `id,name,model_id,group_id/id,operation,domain` | Report access rights are declared as XML `ir.access` records |
| QWeb output | `t-esc` removed, `t-out` required | All report templates use `t-out` |
| `stock.move.name` | Field removed | Test fixtures omit it |
| `ir.actions.report` | No `report_file` field | Report actions declare `report_name` only |
| Product type | `type` is `consu`/`service`/`combo`; stock tracking is `is_storable` | SKU rule keys off `is_storable` |
| `--without-demo` | Boolean, not a value list | Config and scripts pass `--without-demo` |
| Settings UI | `<app>` / `<block>` / `<setting>` inside `//form` | `StockFlow` settings block follows that structure |
| Search view groups | `expand` attribute removed | Ledger search view uses plain `<group>` |
| Report printing | Admin without an external layout gets a layout wizard instead of the PDF | Tests pass `discard_logo_check` |
| Master password | `admin_passwd` is hashed with `pbkdf2_sha512` and `config.save()` rewrites `odoo.conf` | Config is rendered from `config/odoo.conf.template` into the container's writable layer |

### Configuration rendering

`config/odoo.conf.template` is mounted read-only at `/etc/odoo/odoo.conf.template`. The container command renders it to `/etc/odoo/odoo.conf` only when the target has no active `admin_passwd` line:

- Fresh container → image default config (no `admin_passwd`) → rendered from `ODOO_MASTER_PASSWORD`.
- Restart of the same container → writable layer keeps the rendered file → a master password set in the UI survives.
- Recreate → fresh writable layer → rendered again, so `.env` wins.

Mounting the template straight over `odoo.conf` read-only would make `config.save()` fail silently (`config.py:1080`), leaving a UI-set master password in memory only. That was the original cause of the "bad admin password" error.


## Data flow

```
Purchase order ──confirm──▶ Receipt (incoming)
                              └─ validate ─▶ stock.quant ↑ ─▶ stock.move (receipt)
Internal transfer ──approve──▶ validate ─▶ stock.quant ⇄ ─▶ stock.move (internal)
Sales order ──confirm──▶ Delivery (outgoing)
                              └─ validate ─▶ stock.quant ↓ ─▶ stock.move (delivery)
Inventory adjustment ─▶ stock.quant.set ─▶ stock.move (adjustment)
```

Every arrow that touches `stock.quant` passes the negative-stock guard and produces a `stock.move` row, which is what the ledger and the reports read.
