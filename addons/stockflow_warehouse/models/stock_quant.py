from odoo import _, models
from odoo.exceptions import UserError

STOCK_HOLDING_USAGES = ("internal", "transit")


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _stockflow_negative_blocked(self):
        if self.env.context.get("stockflow_allow_negative"):
            return False
        return self.env["stockflow.settings"].stockflow_get_bool("block_negative_stock", True)

    def _update_available_quantity(
        self,
        product_id,
        location_id,
        quantity=False,
        reserved_quantity=False,
        lot_id=None,
        package_id=None,
        owner_id=None,
        in_date=None,
    ):
        result = super()._update_available_quantity(
            product_id,
            location_id,
            quantity=quantity,
            reserved_quantity=reserved_quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            in_date=in_date,
        )
        if not quantity or quantity > 0:
            return result
        if location_id.usage not in STOCK_HOLDING_USAGES or not product_id.is_storable:
            return result
        if not self._stockflow_negative_blocked():
            return result

        quants = self._gather(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=True,
        )
        on_hand = sum(quants.mapped("quantity"))
        if product_id.uom_id.compare(on_hand, 0.0) < 0:
            raise UserError(
                _(
                    "Stock cannot go negative: %(product)s would drop to %(qty)s in %(location)s. "
                    "Receive or transfer stock first.",
                    product=product_id.display_name,
                    qty=product_id.uom_id.round(on_hand),
                    location=location_id.display_name,
                )
            )
        return result
