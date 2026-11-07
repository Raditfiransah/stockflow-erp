from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    stockflow_movement_type = fields.Selection(
        [
            ("receipt", "Receipt"),
            ("delivery", "Delivery"),
            ("internal", "Internal Transfer"),
            ("adjustment", "Inventory Adjustment"),
            ("return", "Return"),
        ],
        string="Movement Type",
        compute="_compute_stockflow_movement_type",
        store=True,
    )

    @api.depends(
        "is_inventory",
        "origin_returned_move_id",
        "picking_id.picking_type_code",
    )
    def _compute_stockflow_movement_type(self):
        for move in self:
            if move.is_inventory:
                move.stockflow_movement_type = "adjustment"
            elif move.origin_returned_move_id:
                move.stockflow_movement_type = "return"
            elif move.picking_id.picking_type_code == "incoming":
                move.stockflow_movement_type = "receipt"
            elif move.picking_id.picking_type_code == "outgoing":
                move.stockflow_movement_type = "delivery"
            elif move.picking_id.picking_type_code == "internal":
                move.stockflow_movement_type = "internal"
            else:
                move.stockflow_movement_type = False
