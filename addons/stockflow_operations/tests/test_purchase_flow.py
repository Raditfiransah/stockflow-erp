from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.vendor = cls.env["res.partner"].create(
            {"name": "PT Supplier Bersih", "supplier_rank": 1}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Dish Soap 1L",
                "type": "consu",
                "is_storable": True,
                "default_code": "SOAP-001",
                "standard_price": 8.0,
                "list_price": 12.0,
            }
        )

    def _manual_receipt(self, qty=3):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "uom_id": self.product.uom_id.id,
                            "location_id": self.env.ref("stock.stock_location_suppliers").id,
                            "location_dest_id": self.warehouse.lot_stock_id.id,
                        },
                    )
                ],
            }
        )

    def test_manual_receipt_is_blocked(self):
        picking = self._manual_receipt()
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = 3
        picking.move_ids.picked = True
        with self.assertRaises(UserError):
            picking.button_validate()

    def test_purchase_receipt_increases_stock(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 10,
                            "price_unit": 8.0,
                            "uom_id": self.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        order.button_confirm()
        picking = order.picking_ids
        self.assertTrue(picking, "A confirmed purchase order must create a receipt.")
        picking.action_assign()
        picking.move_ids.quantity = 10
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product, self.warehouse.lot_stock_id
            ),
            10.0,
        )
