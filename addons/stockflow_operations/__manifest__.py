{
    "name": "StockFlow Operations",
    "version": "20.0.1.0.0",
    "summary": "Purchase and sales integration rules for StockFlow ERP",
    "author": "PT StockFlow Distribusi",
    "license": "LGPL-3",
    "category": "Inventory/Inventory",
    "depends": [
        "purchase",
        "purchase_stock",
        "sale",
        "sale_stock",
        "stockflow_core",
        "stockflow_warehouse",
    ],
    "data": [
        "views/stock_picking_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
}
