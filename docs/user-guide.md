# User guide

## Master data

### Create a product

1. **Inventory → Products → Products → New**.
2. Fill in the name, set **Product Type** to *Goods*, tick **Track Inventory**.
3. Enter a **SKU** in the Internal Reference field. It is saved uppercase and must be unique.
4. Choose a category, set sales price and cost, then save.

A storable product without a SKU cannot be saved. Use **Inventory → Configuration → Products → Products Without SKU** to find products that predate this rule.

### Create a supplier or customer

1. **Contacts → New**.
2. Set the company name.
3. Open the **StockFlow** tab and enter a **Partner Code** (unique per company).
4. Save. Purchase and sales history buttons appear automatically once the partner has orders.

## Purchasing

### Receive goods

1. **Purchase → Orders → New**, pick the vendor, add lines, confirm the order.
2. Open the generated receipt from the smart button on the order.
3. Check the quantities, then **Validate**.

A receipt that is not linked to a confirmed purchase order is rejected. If goods arrive without a PO, create and confirm the PO first.

### Return to supplier

Open the receipt and use **Return**. Returns are exempt from the purchase-order check.

## Sales

### Deliver an order

1. **Sales → Orders → New**, pick the customer, add lines, confirm the order.
2. Open the delivery from the smart button.
3. Check quantities, then **Validate**.

A delivery without a confirmed sales order is rejected. Stock must be available: a delivery that would push a warehouse below zero is blocked with a message naming the product and location.

## Warehouse

### Transfer between locations

1. **Inventory → Operations → Transfers → New**, choose the *Internal* operation type.
2. Set source and destination (they must differ), add products and quantities.
3. Save, then click **Approve Transfer** (Inventory Manager only).
4. Click **Validate**.

Validation is refused without approval, with identical locations, with no lines, or with a quantity of zero or less. Approval details are shown on the **Approval** tab.

### Adjust inventory

1. **Inventory → Operations → Adjustments → Physical Inventory**.
2. Set the counted quantity.
3. Apply.

A downward adjustment that would make an internal location negative is rejected. Receive or transfer stock first.

## Reporting

### Stock Movement Ledger

**Inventory → Reporting → Stock Movement Ledger**. Every validated move, filterable by product, document, partner and movement type. Switch to pivot or graph for totals, and use the list's export for CSV/XLSX.

### PDF reports

**Inventory → Reporting → StockFlow Reports**:

- **Inventory Report** — on-hand, reserved and available by product and location.
- **Sales Report** — quantity and amount by product or customer.
- **Purchasing Report** — quantity and amount by product or supplier.

Each opens a filter dialog; press **Print** to download the PDF.

## Settings

**Settings → StockFlow** controls the four business rules:

- Block negative stock
- Require a confirmed purchase order for receipts
- Require a confirmed sales order for deliveries
- Require approval for internal transfers

Turning a rule off restores plain Odoo behaviour for that rule. Rules are enforced on the server, so they apply to imports and API calls too.

## Database manager

Open **<http://localhost:8070/web/database/manager>** to create, duplicate, back up, restore or delete databases.

The page asks for the **master password**, which is separate from your `admin` login. It comes from `ODOO_MASTER_PASSWORD` in `.env` (default `admin`).

| Situation | What happens |
|---|---|
| You set a password in `.env` and recreate the container | That value becomes the master password |
| You change it with **Set Master Password** in the UI | It sticks across `docker compose restart` |
| You recreate the container | The value from `.env` applies again |
| You see "bad admin password" | The password you typed is wrong; it is not a fault. Check `.env` or reset it there and recreate |
| A banner says the manager is unprotected | The master password is still the default `admin`. Set your own in `.env` |

If you do not need the web manager, set `list_db = False` in `config/odoo.conf.template` and recreate the container. Database creation then only happens through `scripts/init-db.ps1`.

