from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockflowSku(TransactionCase):
    def _create_product(self, code=None, **kwargs):
        vals = {
            "name": "Test Product",
            "type": "consu",
            "is_storable": True,
        }
        if code is not None:
            vals["default_code"] = code
        vals.update(kwargs)
        return self.env["product.template"].create(vals)

    def test_sku_is_normalized(self):
        template = self._create_product("  mop-001  ")
        self.assertEqual(template.default_code, "MOP-001")

    def test_duplicate_sku_is_rejected(self):
        self._create_product("BUCKET-01")
        with self.assertRaises(ValidationError):
            self._create_product("bucket-01")

    def test_storable_product_requires_sku(self):
        with self.assertRaises(ValidationError):
            self._create_product(None)

    def test_service_product_without_sku_is_allowed(self):
        template = self.env["product.template"].create(
            {"name": "Delivery Service", "type": "service"}
        )
        self.assertFalse(template.default_code)
