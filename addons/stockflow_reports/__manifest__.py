{
    "name": "StockFlow Reports",
    "version": "20.0.1.0.0",
    "summary": "Inventory, sales and purchasing reports",
    "author": "PT StockFlow Distribusi",
    "license": "LGPL-3",
    "category": "Inventory/Inventory",
    "depends": ["stockflow_operations", "stockflow_warehouse"],
    "data": [
        "security/stockflow_reports_security.xml",
        "report/stockflow_report_templates.xml",
        "report/stockflow_report_actions.xml",
        "views/stockflow_report_views.xml",
        "views/stockflow_report_menus.xml",
    ],
    "installable": True,
}
