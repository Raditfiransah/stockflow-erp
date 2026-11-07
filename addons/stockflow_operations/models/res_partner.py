from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    stockflow_purchase_count = fields.Integer(
        string="Purchase Orders", compute="_compute_stockflow_history"
    )
    stockflow_sale_count = fields.Integer(
        string="Sales Orders", compute="_compute_stockflow_history"
    )

    @api.depends("name")
    def _compute_stockflow_history(self):
        for partner in self:
            domain = [("partner_id", "child_of", partner.id)]
            partner.stockflow_purchase_count = self.env["purchase.order"].search_count(domain)
            partner.stockflow_sale_count = self.env["sale.order"].search_count(domain)

    def action_stockflow_purchase_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
        action["domain"] = [("partner_id", "child_of", self.id)]
        action["context"] = {"create": False}
        return action

    def action_stockflow_sale_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action["domain"] = [("partner_id", "child_of", self.id)]
        action["context"] = {"create": False}
        return action
