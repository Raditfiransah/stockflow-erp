from odoo import fields, models


class StockflowInventoryReport(models.TransientModel):
    _name = "stockflow.inventory.report"
    _description = "StockFlow Inventory Report"

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company, required=True
    )
    date_to = fields.Date(string="As Of", default=fields.Date.context_today, required=True)
    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouses")
    categ_ids = fields.Many2many("product.category", string="Categories")
    product_ids = fields.Many2many("product.product", string="Products")
    hide_zero = fields.Boolean(string="Hide zero quantities", default=True)

    def _quant_domain(self):
        domain = [("location_id.usage", "in", ("internal", "transit"))]
        if self.warehouse_ids:
            domain.append(("location_id", "child_of", self.warehouse_ids.view_location_id.ids))
        if self.categ_ids:
            domain.append(("product_id.categ_id", "child_of", self.categ_ids.ids))
        if self.product_ids:
            domain.append(("product_id", "in", self.product_ids.ids))
        return domain

    def get_report_data(self):
        self.ensure_one()
        groups = self.env["stock.quant"]._read_group(
            self._quant_domain(),
            ["product_id", "location_id"],
            ["quantity:sum", "reserved_quantity:sum"],
        )
        lines = []
        for product, location, quantity, reserved in groups:
            if self.hide_zero and not quantity:
                continue
            lines.append(
                {
                    "sku": product.default_code or "",
                    "product": product.display_name,
                    "category": product.categ_id.display_name or "",
                    "location": location.display_name,
                    "quantity": quantity,
                    "reserved": reserved,
                    "available": quantity - reserved,
                }
            )
        lines.sort(key=lambda row: (row["product"], row["location"]))
        return {
            "company": self.company_id,
            "currency": self.company_id.currency_id,
            "date_to": self.date_to,
            "lines": lines,
            "total_quantity": sum(row["quantity"] for row in lines),
        }

    def action_print(self):
        return self.env.ref("stockflow_reports.action_report_inventory").report_action(self)
