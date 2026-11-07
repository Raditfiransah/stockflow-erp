from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSalesFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.customer = cls.env["res.partner"].create(
            {"name": "Toko Sumber Rejeki", "customer_rank": 1}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Broom",
                "type": "consu",
                "is_storable": True,
                "default_code": "BRM-001",
                "list_price": 15.0,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 50
        )

    def _manual_delivery(self, qty=3):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "uom_id": self.product.uom_id.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                        },
                    )
                ],
            }
        )

    def test_manual_delivery_is_blocked(self):
        picking = self._manual_delivery()
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = 3
        picking.move_ids.picked = True
        with self.assertRaises(UserError):
            picking.button_validate()

    def test_sales_delivery_decreases_stock(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "price_unit": 15.0,
                            "product_uom_id": self.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        picking = order.picking_ids
        self.assertTrue(picking, "A confirmed sales order must create a delivery.")
        picking.action_assign()
        picking.move_ids.quantity = 5
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product, self.warehouse.lot_stock_id
            ),
            45.0,
        )

    def test_partner_history_actions(self):
        action = self.customer.action_stockflow_sale_history()
        self.assertEqual(action["res_model"], "sale.order")
        self.assertEqual(action["domain"], [("partner_id", "child_of", self.customer.id)])
