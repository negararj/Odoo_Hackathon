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
    # employee_skills = fields.Char(string='My Skills', help='Comma-separated list of your skills (e.g., Python, Leadership, Design)')
    #project_ids = fields.Many2many('project.project', string='Projects', help='Projects associated with this employee')
    #project_task_ids = fields.Many2many('project.task', string='Tasks', help='Tasks associated with this employee')

    @api.depends('money_O2')
    def _compute_badge(self):
        for employee in self:
            if employee.money_O2 >= 100:
                employee.badge = 'gold'
            elif employee.money_O2 >= 50:
                employee.badge = 'silver'
            else:
                employee.badge = 'bronze'
    
    # Add custom fields for CSR and Sustainability here
    # Example fields (you can customize these):
    # csr_volunteer_hours = fields.Float(string='CSR Volunteer Hours')
    # sustainability_training_completed = fields.Boolean(string='Sustainability Training Completed')

