from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stockflow_block_negative_stock = fields.Boolean(
        string="Block negative stock",
        config_parameter="stockflow.block_negative_stock",
        default=True,
        help="Prevent internal locations from holding a negative quantity.",
    )
    stockflow_require_po_for_receipt = fields.Boolean(
        string="Require a confirmed purchase order for receipts",
        config_parameter="stockflow.require_po_for_receipt",
        default=True,
    )
    stockflow_require_so_for_delivery = fields.Boolean(
        string="Require a confirmed sales order for deliveries",
        config_parameter="stockflow.require_so_for_delivery",
        default=True,
    )
    stockflow_require_internal_transfer_approval = fields.Boolean(
        string="Require approval for internal transfers",
        config_parameter="stockflow.require_internal_transfer_approval",
        default=True,
    )
