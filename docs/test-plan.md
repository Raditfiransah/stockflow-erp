# Test plan

## Automated tests

Run with:

```powershell
.\scripts\test.ps1
```

Result on a clean `stockflow_test` database: **22 tests, 0 failed, 0 errors**.

| Module | Test | Asserts |
|---|---|---|
| `stockflow_core` | `test_sku_is_normalized` | `"  mop-001  "` stored as `MOP-001` |
| | `test_duplicate_sku_is_rejected` | Second product with the same SKU raises `ValidationError` |
| | `test_storable_product_requires_sku` | Storable product without SKU raises `ValidationError` |
| | `test_service_product_without_sku_is_allowed` | Service products may have no SKU |
| `stockflow_warehouse` | `test_negative_update_is_blocked` | `-3` on a stock location raises `UserError` |
| | `test_stock_can_go_down_to_zero` | `+5` then `-5` leaves 0 and is allowed |
| | `test_supplier_location_may_go_negative` | Supplier location reaches `-10` |
| | `test_bypass_context_allows_negative` | `stockflow_allow_negative` context bypasses the guard |
| | `test_transfer_requires_approval` | Unapproved internal transfer cannot be validated |
| | `test_approved_transfer_is_validated` | Approved transfer completes and destination holds 5 |
| | `test_same_location_is_rejected` | Identical source and destination raise `UserError` |
| | `test_movement_type_is_traced` | Move is tagged `internal` |
| `stockflow_operations` | `test_manual_receipt_is_blocked` | Receipt without a PO raises `UserError` |
| | `test_purchase_receipt_increases_stock` | PO → receipt leaves 10 on hand |
| | `test_manual_delivery_is_blocked` | Delivery without an SO raises `UserError` |
| | `test_sales_delivery_decreases_stock` | SO → delivery leaves 45 of 50 |
| | `test_partner_history_actions` | Sales history action targets `sale.order` with a partner domain |
| `stockflow_reports` | `test_inventory_report_data` | Total on hand equals 25, SKU present |
| | `test_inventory_report_action` | Action type is `ir.actions.report` with the right template |
| | `test_sales_report_totals` | 5 units, 50.00 total |
| | `test_purchase_report_totals` | 10 units, 80.00 total |
| | `test_report_actions_exist` | All three reports are `qweb-pdf` |

## Manual verification performed

| Check | Command / action | Result |
|---|---|---|
| Stack starts | `docker compose up -d` | DB healthy, Odoo started |
| Modules install | `-i stockflow_core,stockflow_warehouse,stockflow_operations,stockflow_reports` | All loaded |
| Web UI responds | `curl http://localhost:8070/web/login` | `200` |
| Demo data loads | `-i stockflow_demo` | 12 products, 5 suppliers, 5 customers, 3 warehouses |
| Settings defaults | `stockflow_get_bool` for all four keys | All `True` |
| Inventory PDF | `_render_qweb_pdf` on the inventory report | 22,411 bytes, contains SKU and quantity |
| Sales PDF | `_render_qweb_pdf` | 20,592 bytes |
| Purchasing PDF | `_render_qweb_pdf` | 20,439 bytes |

## UAT checklist

Run against the demo database and tick each item.

| # | Scenario | Expected | Done |
|---|---|---|---|
| 1 | Create a product with an existing SKU | Save blocked with "SKU … is already used" | ☐ |
| 2 | Create a storable product with no SKU | Save blocked with "must have a SKU" | ☐ |
| 3 | Confirm a PO, receive the goods | Receipt validates, stock increases | ☐ |
| 4 | Validate a receipt with no PO | Blocked with "must be linked to a confirmed purchase order" | ☐ |
| 5 | Confirm an SO, deliver the goods | Delivery validates, stock decreases | ☐ |
| 6 | Deliver more than available stock | Blocked with a negative-stock message | ☐ |
| 7 | Validate a delivery with no SO | Blocked with "must be linked to a confirmed sales order" | ☐ |
| 8 | Create an internal transfer and validate without approval | Blocked | ☐ |
| 9 | Approve, then validate the internal transfer | Completes, stock moves between locations | ☐ |
| 10 | Set an internal location to a negative counted quantity | Adjustment blocked | ☐ |
| 11 | Open the Stock Movement Ledger | Receipts, deliveries, transfers and adjustments listed with references | ☐ |
| 12 | Print the inventory, sales and purchasing reports | PDFs open with correct totals | ☐ |
| 13 | Open a partner with orders | Purchase and sales smart buttons show counts | ☐ |
| 14 | Open any picking chatter | State changes and approvals recorded | ☐ |

## Known limitations

- Variants are supported, but the SKU rule is validated per variant; a product with many variants needs one SKU per variant.
- The reports read current quantities; there is no historical "as of date" reconstruction. The `date_to` filter on the inventory report labels the report rather than replaying past movements.
- Automated tests run on a fresh database; they are not part of the running server's cron workload.
