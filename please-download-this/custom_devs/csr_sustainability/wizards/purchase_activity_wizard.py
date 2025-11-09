# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseActivityWizard(models.TransientModel):
    _name = 'csr.purchase.activity.wizard'
    _description = 'Wizard to Purchase CSR Activity'

    activity_id = fields.Many2one(
        'csr.activity',
        string='Activity',
        required=True,
        readonly=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )
    xp_cost = fields.Float(string='XP Cost', related='activity_id.xp', readonly=True)
    o2_value = fields.Float(string='O2 Value', related='activity_id.value', readonly=True)
    current_xp = fields.Float(string='Your Current XP', compute='_compute_current_xp', readonly=True)
    can_purchase = fields.Boolean(string='Can Purchase', compute='_compute_can_purchase', readonly=True)

    @api.depends('employee_id', 'xp_cost')
    def _compute_current_xp(self):
        for wizard in self:
            if wizard.employee_id:
                # XP is stored as sustainability_points
                wizard.current_xp = wizard.employee_id.sudo().sustainability_points or 0
            else:
                wizard.current_xp = 0

    @api.depends('current_xp', 'xp_cost')
    def _compute_can_purchase(self):
        for wizard in self:
            wizard.can_purchase = wizard.current_xp >= wizard.xp_cost

    @api.model
    def default_get(self, fields_list):
        res = super(PurchaseActivityWizard, self).default_get(fields_list)
        user = self.env.user
        
        # Get activity from context
        if 'activity_id' in fields_list and not res.get('activity_id'):
            if self.env.context.get('active_id') and self.env.context.get('active_model') == 'csr.activity':
                res['activity_id'] = self.env.context.get('active_id')
        
        # Get employee for current user
        if 'employee_id' in fields_list:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            if not employee:
                employee = self.env['hr.employee'].sudo().search([
                    ('name', 'ilike', user.name)
                ], limit=1)
            if employee:
                res['employee_id'] = employee.id
        
        return res

    def action_purchase(self):
        """Purchase the activity"""
        self.ensure_one()
        
        if not self.can_purchase:
            raise UserError(_('You do not have enough XP to purchase this activity. You need %s XP but only have %s XP.') % (
                self.xp_cost, self.current_xp
            ))
        
        # Create purchase record
        purchase = self.env['csr.activity.purchase'].sudo().create({
            'activity_id': self.activity_id.id,
            'employee_id': self.employee_id.id,
            'xp_paid': self.xp_cost,
            'o2_received': self.o2_value,
        })
        
        # Update employee's XP (sustainability_points) and O2 (money_O2)
        self.employee_id.sudo().write({
            'sustainability_points': self.employee_id.sustainability_points - self.xp_cost,
            'money_O2': (self.employee_id.money_O2 or 0) + self.o2_value,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('You have successfully purchased "%s"! You received %s O2.', self.activity_id.name, self.o2_value),
                'type': 'success',
                'sticky': False,
            }
        }

