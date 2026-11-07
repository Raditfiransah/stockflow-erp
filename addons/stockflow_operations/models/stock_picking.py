from odoo import _, models
from odoo.exceptions import UserError

OPEN_ORDER_STATES = ("purchase", "done")
CONFIRMED_SALE_STATES = ("sale", "done")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for picking in self:
            picking._stockflow_check_source_document()
        return super().button_validate()

    def _stockflow_check_source_document(self):
        self.ensure_one()
        if self.return_id:
            return
        settings = self.env["stockflow.settings"]
        if self.picking_type_code == "incoming":
            if not settings.stockflow_get_bool("require_po_for_receipt", True):
                return
            orders = self.move_ids.purchase_line_id.order_id
            if not orders or any(order.state not in OPEN_ORDER_STATES for order in orders):
                raise UserError(
                    _(
                        "Receipt %(name)s must be linked to a confirmed purchase order.",
                        name=self.name,
                    )
                )
        elif self.picking_type_code == "outgoing":
            if not settings.stockflow_get_bool("require_so_for_delivery", True):
                return
            orders = self.move_ids.sale_line_id.order_id
            if not orders or any(order.state not in CONFIRMED_SALE_STATES for order in orders):
                raise UserError(
                    _(
                        "Delivery %(name)s must be linked to a confirmed sales order.",
                        name=self.name,
                    )
                )
