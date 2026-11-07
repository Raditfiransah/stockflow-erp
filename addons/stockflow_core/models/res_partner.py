from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    stockflow_code = fields.Char(
        string="Partner Code",
        index=True,
        copy=False,
        help="Internal identifier used by PT StockFlow Distribusi.",
    )

    @api.constrains("stockflow_code", "company_id")
    def _check_stockflow_code(self):
        for partner in self:
            code = (partner.stockflow_code or "").strip()
            if not code:
                continue
            duplicate = self.search_count(
                [
                    ("stockflow_code", "=", code),
                    ("company_id", "=", partner.company_id.id),
                    ("id", "!=", partner.id),
                ],
                limit=1,
            )
            if duplicate:
                raise ValidationError(
                    _("Partner code %(code)s is already used.", code=code)
                )
