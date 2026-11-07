{
    "name": "StockFlow Core",
    "version": "20.0.1.0.0",
    "summary": "Master data rules, SKU policy and StockFlow settings",
    "author": "PT StockFlow Distribusi",
    "license": "LGPL-3",
    "category": "Inventory/Inventory",
    "depends": ["base", "product", "stock"],
    "data": [
        "data/stockflow_config_data.xml",
        "data/product_category_data.xml",
        "views/product_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": True,
}
