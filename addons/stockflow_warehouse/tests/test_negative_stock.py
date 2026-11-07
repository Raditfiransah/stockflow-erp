from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNegativeStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Floor Cleaner",
                "type": "consu",
                "is_storable": True,
                "default_code": "CLN-001",
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

    def test_negative_update_is_blocked(self):
        with self.assertRaises(UserError):
            self.env["stock.quant"]._update_available_quantity(
                self.product, self.stock_location, -3
            )

    def test_stock_can_go_down_to_zero(self):
        quants = self.env["stock.quant"]
        quants._update_available_quantity(self.product, self.stock_location, 5)
        quants._update_available_quantity(self.product, self.stock_location, -5)
        self.assertEqual(
            quants._get_available_quantity(self.product, self.stock_location), 0.0
        )

    def test_supplier_location_may_go_negative(self):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.supplier_location, -10
        )
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product, self.supplier_location, allow_negative=True
            ),
            -10.0,
        )

    def test_bypass_context_allows_negative(self):
        self.env["stock.quant"].with_context(stockflow_allow_negative=True)._update_available_quantity(
            self.product, self.stock_location, -4
        )
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product, self.stock_location, allow_negative=True
            ),
            -4.0,
        )
