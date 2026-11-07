from datetime import datetime, time

from odoo import fields, models


class StockflowSalesReport(models.TransientModel):
    _name = "stockflow.sales.report"
    _description = "StockFlow Sales Report"

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company, required=True
    )
    date_from = fields.Date(
        string="From",
        default=lambda self: fields.Date.context_today(self).replace(day=1),
        required=True,
    )
    date_to = fields.Date(string="To", default=fields.Date.context_today, required=True)
    partner_ids = fields.Many2many("res.partner", string="Customers")
    product_ids = fields.Many2many("product.product", string="Products")
    group_by = fields.Selection(
        [("product", "Product"), ("customer", "Customer")],
        string="Group By",
        default="product",
        required=True,
    )

    def _line_domain(self):
        domain = [
            ("order_id.state", "in", ("sale", "done")),
            ("order_id.date_order", ">=", datetime.combine(self.date_from, time.min)),
            ("order_id.date_order", "<=", datetime.combine(self.date_to, time.max)),
        ]
        if self.partner_ids:
            domain.append(("order_id.partner_id", "in", self.partner_ids.ids))
        if self.product_ids:
            domain.append(("product_id", "in", self.product_ids.ids))
        return domain

    def get_report_data(self):
        self.ensure_one()
        groupby = "order_id.partner_id" if self.group_by == "customer" else "product_id"
        groups = self.env["sale.order.line"]._read_group(
            self._line_domain(),
            [groupby],
            ["product_uom_qty:sum", "price_subtotal:sum"],
        )
        lines = [
            {
                "label": group.display_name if group else "",
                "quantity": quantity,
                "amount": amount,
            }
            for group, quantity, amount in groups
        ]
        lines.sort(key=lambda row: row["label"])
        return {
            "company": self.company_id,
            "currency": self.company_id.currency_id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "group_label": "Customer" if self.group_by == "customer" else "Product",
            "lines": lines,
            "total_quantity": sum(row["quantity"] for row in lines),
            "total_amount": sum(row["amount"] for row in lines),
        }

    def action_print(self):
        return self.env.ref("stockflow_reports.action_report_sales").report_action(self)
