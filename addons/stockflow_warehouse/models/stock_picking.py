from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    stockflow_approval_required = fields.Boolean(
        string="Approval Required",
        compute="_compute_stockflow_approval_required",
    )
    stockflow_approved = fields.Boolean(string="Approved", copy=False, tracking=True)
    stockflow_approved_by = fields.Many2one(
        "res.users", string="Approved By", copy=False, readonly=True
    )
    stockflow_approved_on = fields.Datetime(
        string="Approved On", copy=False, readonly=True
    )
    stockflow_requested_by = fields.Many2one(
        "res.users",
        string="Requested By",
        copy=False,
        default=lambda self: self.env.user,
    )

    @api.depends("picking_type_code")
    def _compute_stockflow_approval_required(self):
        enabled = self.env["stockflow.settings"].stockflow_get_bool(
            "require_internal_transfer_approval", True
        )
        for picking in self:
            picking.stockflow_approval_required = bool(
                enabled and picking.picking_type_code == "internal"
            )

    def action_stockflow_approve(self):
        for picking in self:
            if picking.picking_type_code != "internal":
                raise UserError(_("Only internal transfers need approval."))
            if picking.state in ("done", "cancel"):
                raise UserError(_("This transfer is already closed."))
        self.write(
            {
                "stockflow_approved": True,
                "stockflow_approved_by": self.env.user.id,
                "stockflow_approved_on": fields.Datetime.now(),
            }
        )
        return True

    def action_stockflow_reset_approval(self):
        self.write(
            {
                "stockflow_approved": False,
                "stockflow_approved_by": False,
                "stockflow_approved_on": False,
            }
        )
        return True

    def button_validate(self):
        for picking in self:
            picking._stockflow_check_internal_transfer()
        return super().button_validate()

    def _stockflow_check_internal_transfer(self):
        self.ensure_one()
        if self.picking_type_code != "internal":
            return
        if not self.stockflow_approval_required:
            return
        if self.location_id == self.location_dest_id:
            raise UserError(
                _("The source and destination locations of an internal transfer must differ.")
            )
        if not self.move_ids:
            raise UserError(_("Add at least one product before validating the transfer."))
        if any(move.uom_id.compare(move.product_uom_qty, 0.0) <= 0 for move in self.move_ids):
            raise UserError(_("Transfer quantities must be greater than zero."))
        if not self.stockflow_approved:
            raise UserError(
                _("Transfer %(name)s needs approval before it can be validated.", name=self.name)
            )
