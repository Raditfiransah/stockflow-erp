from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestInternalTransfer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Glass Cleaner",
                "type": "consu",
                "is_storable": True,
                "default_code": "CLN-002",
            }
        )
        cls.source = cls.warehouse.lot_stock_id
        cls.destination = cls.env["stock.location"].create(
            {
                "name": "Rack B",
                "location_id": cls.source.id,
                "usage": "internal",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.source, 20)

    def _create_transfer(self, qty=5):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.int_type_id.id,
                "location_id": self.source.id,
                "location_dest_id": self.destination.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "uom_id": self.product.uom_id.id,
                            "location_id": self.source.id,
                            "location_dest_id": self.destination.id,
                        },
                    )
                ],
            }
        )

    def _ready_transfer(self, qty=5):
        picking = self._create_transfer(qty)
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity = qty
        picking.move_ids.picked = True
        return picking

    def test_transfer_requires_approval(self):
        picking = self._ready_transfer()
        self.assertTrue(picking.stockflow_approval_required)
        self.assertFalse(picking.stockflow_approved)
        with self.assertRaises(UserError):
            picking.button_validate()

    def test_approved_transfer_is_validated(self):
        picking = self._ready_transfer()
        picking.action_stockflow_approve()
        self.assertTrue(picking.stockflow_approved)
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product, self.destination
            ),
            5.0,
        )

    def test_same_location_is_rejected(self):
        picking = self._create_transfer()
        picking.location_dest_id = picking.location_id
        picking.action_stockflow_approve()
        with self.assertRaises(UserError):
            picking.button_validate()

    def test_movement_type_is_traced(self):
        picking = self._ready_transfer()
        picking.action_stockflow_approve()
        picking.button_validate()
        self.assertEqual(picking.move_ids.stockflow_movement_type, "internal")
