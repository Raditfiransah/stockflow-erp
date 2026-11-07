# Business rules

Each rule from the BRD, where it is enforced, and how to change it.

| # | Rule | Enforced in | Setting | Test |
|---|---|---|---|---|
| 1 | Every product has a unique SKU | `product.template._stockflow_validate_sku`, `product.product._check_stockflow_sku_unique` | — | `stockflow_core` / `test_sku.py` |
| 2 | Inventory must not go negative | `stock.quant._update_available_quantity` | `stockflow.block_negative_stock` | `stockflow_warehouse` / `test_negative_stock.py` |
| 3 | Every stock movement is recorded and traceable | `stock.move.stockflow_movement_type`, ledger views | — | `stockflow_warehouse` / `test_internal_transfer.py::test_movement_type_is_traced` |
| 4 | Internal transfers have proper statuses and approval | `stock.picking._stockflow_check_internal_transfer`, `action_stockflow_approve` | `stockflow.require_internal_transfer_approval` | `stockflow_warehouse` / `test_internal_transfer.py` |
| 5 | Purchase orders must be confirmed before receiving | `stock.picking._stockflow_check_source_document` | `stockflow.require_po_for_receipt` | `stockflow_operations` / `test_purchase_flow.py` |
| 6 | Deliveries must link to a valid sales order | `stock.picking._stockflow_check_source_document` | `stockflow.require_so_for_delivery` | `stockflow_operations` / `test_sales_flow.py` |
| 7 | Transactions keep an activity history | `mail.thread` / `mail.activity.mixin` on the standard documents | — | Odoo native |

## Details

### SKU

- Stored uppercase, trimmed. `"  mop-001  "` becomes `MOP-001`.
- Duplicates are rejected across the whole database, including archived products.
- Required for `is_storable` products only; services may have no SKU.
- Data imports can bypass the check with the `stockflow_skip_sku_check` context key.

### Negative stock

- Applies to locations with usage `internal` or `transit`.
- Supplier, customer and inventory-loss locations may go negative, because that is how Odoo models a counterpart.
- The guard runs after the quant write and raises before the transaction commits, so nothing is left half-applied.
- System code that legitimately needs a negative quant can pass `stockflow_allow_negative` in the context.

### Internal transfers

- Approval is required when the setting is on and the picking type code is `internal`.
- The approver and timestamp are stored on the transfer.
- Validation is blocked when source equals destination, when there are no lines, when a line has a quantity of zero or less, or when approval is missing.
- Cancelled and done transfers cannot be approved.

### Receipts and deliveries

- Checked on `button_validate()`, so it covers both the standard Validate button and API calls.
- Returns created through `return_id` are exempt: returning goods must not require a new purchase or sales order.
- With the setting off, Odoo's default behaviour applies.

### Activity history

Standard Odoo chatter is enabled on `stock.picking`, `purchase.order`, `sale.order` and `product.template`. Tracked fields include state, partner, scheduled date and quantities. Internal transfers also track `stockflow_approved`.
