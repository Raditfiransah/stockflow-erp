from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockflowReports(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "CV Mitra Bersih", "supplier_rank": 1, "customer_rank": 1}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Mop Head",
                "type": "consu",
                "is_storable": True,
                "default_code": "MOP-HEAD",
                "standard_price": 8.0,
                "list_price": 10.0,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 25
        )

    def test_inventory_report_data(self):
        wizard = self.env["stockflow.inventory.report"].create(
            {"date_to": fields.Date.today()}
        )
        data = wizard.get_report_data()
        self.assertEqual(data["total_quantity"], 25.0)
        self.assertTrue(data["lines"])
        self.assertEqual(data["lines"][0]["sku"], "MOP-HEAD")

    def test_inventory_report_action(self):
        wizard = self.env["stockflow.inventory.report"].create({})
        action = wizard.with_context(discard_logo_check=True).action_print()
        self.assertEqual(action["type"], "ir.actions.report")
        self.assertEqual(
            action["report_name"], "stockflow_reports.report_inventory_document"
        )

    def test_sales_report_totals(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "price_unit": 10.0,
                            "product_uom_id": self.product.uom_id.id,
                            "name": self.product.display_name,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        wizard = self.env["stockflow.sales.report"].create({})
        data = wizard.get_report_data()
        self.assertEqual(data["total_quantity"], 5.0)
        self.assertEqual(data["total_amount"], 50.0)

    def test_purchase_report_totals(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 10,
                            "price_unit": 8.0,
                            "uom_id": self.product.uom_id.id,
                            "name": self.product.display_name,
                        },
                    )
                ],
            }
        )
        order.button_confirm()
        wizard = self.env["stockflow.purchase.report"].create({})
        data = wizard.get_report_data()
        self.assertEqual(data["total_quantity"], 10.0)
        self.assertEqual(data["total_amount"], 80.0)

    def test_report_actions_exist(self):
        for xmlid in (
            "stockflow_reports.action_report_inventory",
            "stockflow_reports.action_report_sales",
            "stockflow_reports.action_report_purchase",
        ):
            report = self.env.ref(xmlid)
            self.assertEqual(report.report_type, "qweb-pdf")
