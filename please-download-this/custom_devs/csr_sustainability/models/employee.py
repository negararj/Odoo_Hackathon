# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    sustainability_points = fields.Integer(string='Sustainability Points', help='XP points that can be used to purchase activities')
    badge = fields.Selection([
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    ], string='Badge', compute='_compute_badge')
    money_O2 = fields.Float(string='Money O2', help='O2 value earned from purchasing activities')
    activity_purchase_ids = fields.One2many('csr.activity.purchase', 'employee_id', string='Activity Purchases')
    activity_purchase_count = fields.Integer(string='Purchase Count', compute='_compute_activity_purchase_count')
    
    @api.depends('activity_purchase_ids')
    def _compute_activity_purchase_count(self):
        for employee in self:
            employee.activity_purchase_count = len(employee.activity_purchase_ids)

    @api.depends('money_O2')
    def _compute_badge(self):
        for employee in self:
            if employee.money_O2 >= 100:
                employee.badge = 'gold'
            elif employee.money_O2 >= 50:
                employee.badge = 'silver'
            else:
                employee.badge = 'bronze'
    
    @api.depends('money_O2')
    def _compute_leaderboard_rank(self):
        """Compute the rank of employees based on O2 currency"""
        # Get all employees with their O2 values
        all_employees = self.env['hr.employee'].search([])
        
        # Create a list of (id, money_O2) tuples and sort by O2 descending
        employee_o2_list = [(emp.id, emp.money_O2) for emp in all_employees]
        employee_o2_list.sort(key=lambda x: x[1], reverse=True)
        
        # Create rank dictionary
        rank_dict = {}
        current_rank = 1
        prev_o2 = None
        
        for emp_id, o2_value in employee_o2_list:
            # If O2 is different from previous, update rank
            if prev_o2 is not None and o2_value < prev_o2:
                current_rank = len([(eid, o2) for eid, o2 in employee_o2_list if o2 > o2_value]) + 1
            rank_dict[emp_id] = current_rank
            prev_o2 = o2_value
        
        # Assign ranks to current records
        for employee in self:
            employee.leaderboard_rank = rank_dict.get(employee.id, 0)
    
    leaderboard_rank = fields.Integer(string='Rank', compute='_compute_leaderboard_rank', store=False, help='Rank in the leaderboard based on O2 currency')


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

