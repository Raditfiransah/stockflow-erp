from odoo import models


class StockflowSettings(models.AbstractModel):
    _name = "stockflow.settings"
    _description = "StockFlow configuration helpers"

    def stockflow_get_bool(self, key, default=True):
        return self.env["ir.config_parameter"].sudo().get_bool(f"stockflow.{key}", default)
