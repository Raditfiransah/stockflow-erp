# BRD traceability

## 2. Project objectives

| Objective | Delivered by |
|---|---|
| Centralise product, supplier and customer information | `product`, `res.partner` extended in `stockflow_core`; partner code and history in `stockflow_operations` |
| Improve inventory accuracy and warehouse operations | Negative-stock guard, internal transfer approval, movement ledger |
| Integrate purchasing, sales and stock movements | `stockflow_operations` validates receipts against POs and deliveries against SOs |
| Provide reliable operational reports | `stockflow_reports` wizards and PDFs, plus the native ledger pivot/graph |
| Reduce manual processes and inventory errors | Automated validation at document confirmation and picking validation |

## 3. Functional requirements

| Module | Requirement | Where |
|---|---|---|
| Product Management | Products, SKU, categories, pricing | Odoo `product` + `stockflow_core` SKU rules and seed categories |
| Supplier Management | Supplier information and purchase history | `res.partner` `supplier_rank`, `stockflow_code`, purchase history button |
| Customer Management | Customer information and sales history | `res.partner` `customer_rank`, `stockflow_code`, sales history button |
| Purchasing | Purchase orders and goods receipts | Odoo `purchase` + `purchase_stock`, guarded by `stockflow_operations` |
| Inventory | Incoming, outgoing and adjusted stock | Odoo `stock` + `stockflow_warehouse` movement types |
| Warehouse | Multiple warehouses and internal transfers | Odoo `stock` multi-warehouse + internal transfer approval |
| Sales | Sales orders, deliveries, customer transactions | Odoo `sale` + `sale_stock`, guarded by `stockflow_operations` |
| Reporting | Inventory, sales and purchasing reports | `stockflow_reports` |

## 4. Business process

| Step | System behaviour |
|---|---|
| 1. Purchasing creates a PO | `purchase.order` with vendor and lines |
| 2. Warehouse receives goods and updates inventory | Receipt validated only when linked to a confirmed PO; stock increases |
| 3. Sales creates an order | `sale.order` with customer and lines |
| 4. Warehouse prepares and delivers | Delivery validated only when linked to a confirmed SO; stock decreases |
| 5. Inventory updated through validated operations | All changes pass `stock.quant._update_available_quantity`, so the guard applies |
| 6. Managers monitor through reports | Ledger + three PDF reports |

## 5. Business rules

| Rule | Implementation | Test |
|---|---|---|
| Unique SKU | Template + variant validation, uppercase normalisation | `test_sku.py` (4 tests) |
| No negative inventory | Quant guard on internal/transit locations | `test_negative_stock.py` (4 tests) |
| Every movement recorded and traceable | `stockflow_movement_type`, ledger with product/location/partner/date | `test_internal_transfer.py::test_movement_type_is_traced` |
| Internal transfers have proper statuses | Standard states + approval gate | `test_internal_transfer.py` (4 tests) |
| PO confirmed before receiving | Receipt validation check | `test_purchase_flow.py` (2 tests) |
| Delivery linked to valid SO | Delivery validation check | `test_sales_flow.py` (3 tests) |
| Transactions maintain activity history | Odoo chatter with tracking | Odoo native |

## 6. Technical constraints

| Constraint | Status |
|---|---|
| Odoo 20 Community | `odoo:20.0` |
| Python and Odoo ORM | All custom code is ORM-based, no raw SQL in business logic |
| PostgreSQL | `postgres:16` |
| Docker and Docker Compose | `docker-compose.yml` with health-checked DB |
| Extend existing modules where possible | Four modules, all using `_inherit`; no core patches |

## 7. Out of scope (MVP)

Minimum stock alerts, demand forecasting, stockout prediction and advanced analytics dashboards are not implemented. The movement ledger and quant data provide the foundation for them.

## 8. Acceptance criteria

| Criterion | Verification |
|---|---|
| Manage products, suppliers, customers | Product and partner forms, demo data installs 12 products and 10 partners |
| Manage purchasing, sales, multi-warehouse inventory | PO → receipt and SO → delivery flows tested; 3 warehouses in demo |
| Accurate and traceable stock movements | Negative-stock guard + movement ledger |
| Operational reports | Three PDF reports render with live data |

Acceptance evidence is recorded in `docs/test-plan.md`.
