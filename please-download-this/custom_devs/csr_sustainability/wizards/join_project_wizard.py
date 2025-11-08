# -*- coding: utf-8 -*-
from odoo import api, fields, models


class JoinProjectWizard(models.TransientModel):
    _name = 'csr.join.project.wizard'
    _description = 'Wizard to Join Sustainability Project'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        domain=[('is_sustainability', '=', True)]
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )
    message = fields.Text(string='Message', help='Optional message when joining the project')

    @api.model
    def default_get(self, fields_list):
        """Override default_get to ensure employee is always set for the current user"""
        res = super(JoinProjectWizard, self).default_get(fields_list)
        user = self.env.user
        
        # Try to find employee linked to user
        # Use sudo() to bypass access restrictions when searching for employee
        if 'employee_id' in fields_list:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            if not employee:
                # Try to find by name matching
                employee = self.env['hr.employee'].sudo().search([
                    ('name', 'ilike', user.name)
                ], limit=1)
            if employee:
                res['employee_id'] = employee.id
        
        # Set project from context if available
        if 'project_id' in fields_list and not res.get('project_id'):
            if self.env.context.get('active_id') and self.env.context.get('active_model') == 'project.project':
                res['project_id'] = self.env.context.get('active_id')
        
        return res

    def action_join_project(self):
        """Add employee to the project"""
        self.ensure_one()
        if self.project_id and self.employee_id:
            # Add employee to project if not already added
            # Use sudo() to allow employees to add themselves to projects
            if self.employee_id not in self.project_id.employee_ids:
                self.project_id.sudo().write({
                    'employee_ids': [(4, self.employee_id.id)]
                })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': f'You have successfully joined {self.project_id.name}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Info',
                        'message': 'You are already a member of this project',
                        'type': 'warning',
                        'sticky': False,
                    }
                }
        return {'type': 'ir.actions.act_window_close'}

