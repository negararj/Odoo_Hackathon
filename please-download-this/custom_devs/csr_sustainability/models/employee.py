# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    sustainability_points = fields.Integer(string='Sustainability Points')
    badge = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ], string='Badge', compute='_compute_badge')
    money_O2 = fields.Float(string='Money O2')

    @api.depends('money_O2')
    def _compute_badge(self):
        for employee in self:
            if employee.money_O2 >= 100:
                employee.badge = 'gold'
            elif employee.money_O2 >= 50:
                employee.badge = 'silver'
            else:
                employee.badge = 'bronze'


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    
    # Add custom fields to public model so they're accessible to regular users
    sustainability_points = fields.Integer(string='Sustainability Points', related='employee_id.sustainability_points', readonly=True)
    badge = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ], string='Badge', related='employee_id.badge', readonly=True)
    money_O2 = fields.Float(string='Money O2', related='employee_id.money_O2', readonly=True)

