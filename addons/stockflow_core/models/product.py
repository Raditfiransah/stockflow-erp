from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def _normalize_sku(value):
    return (value or "").strip().upper()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "default_code" in vals:
                vals["default_code"] = _normalize_sku(vals["default_code"])
        templates = super().create(vals_list)
        templates._stockflow_validate_sku()
        return templates

    def write(self, vals):
        if "default_code" in vals:
            vals = dict(vals, default_code=_normalize_sku(vals["default_code"]))
        res = super().write(vals)
        if {"default_code", "is_storable", "type"} & set(vals):
            self._stockflow_validate_sku()
        return res

    def _stockflow_validate_sku(self):
        if self.env.context.get("stockflow_skip_sku_check"):
            return
        for template in self:
            code = template.default_code
            if template.is_storable and not code:
                raise ValidationError(
                    _(
                        "Product %(product)s is tracked in inventory and must have a SKU.",
                        product=template.display_name,
                    )
                )
            if not code:
                continue
            duplicate = self.env["product.template"].with_context(active_test=False).search_count(
                [("default_code", "=", code), ("id", "!=", template.id)], limit=1
            )
            if duplicate:
                raise ValidationError(
                    _("SKU %(code)s is already used by another product.", code=code)
                )


class ProductProduct(models.Model):
    _inherit = "product.product"

    stockflow_sku_missing = fields.Boolean(
        compute="_compute_stockflow_sku_missing",
        string="SKU Missing",
    )

    @api.depends("default_code", "is_storable")
    def _compute_stockflow_sku_missing(self):
        for product in self:
            product.stockflow_sku_missing = bool(
                product.is_storable and not (product.default_code or "").strip()
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "default_code" in vals:
                vals["default_code"] = _normalize_sku(vals["default_code"])
        # The template is created before the variant's own fields are applied, so the
        # template-level SKU rule must wait until the variant exists.
        products = super(ProductProduct, self.with_context(stockflow_skip_sku_check=True)).create(
            vals_list
        )
        products.product_tmpl_id._stockflow_validate_sku()
        return products

    def write(self, vals):
        if "default_code" in vals:
            vals = dict(vals, default_code=_normalize_sku(vals["default_code"]))
        return super().write(vals)

    @api.constrains("default_code")
    def _check_stockflow_sku_unique(self):
        if self.env.context.get("stockflow_skip_sku_check"):
            return
        for product in self:
            code = product.default_code
            if not code:
                continue
            duplicate = self.with_context(active_test=False).search_count(
                [("default_code", "=", code), ("id", "!=", product.id)], limit=1
            )
            if duplicate:
                raise ValidationError(
                    _("SKU %(code)s is already used by another product.", code=code)
                )
