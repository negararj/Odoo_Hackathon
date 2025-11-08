# -*- coding: utf-8 -*-
from odoo import api, fields, models


class JoinProjectWizard(models.TransientModel):
    _name = 'csr.join.project.wizard'
    _description = 'Wizard to Join Sustainability Project'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        domain=[('is_sustainability', '=', True)],
        default=lambda self: self._default_project()
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self._default_employee()
    )
    message = fields.Text(string='Message', help='Optional message when joining the project')

    def _default_project(self):
        """Get project from context if available"""
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'project.project':
            return self.env.context.get('active_id')
        return False

    def _default_employee(self):
        """Get the current user's employee record"""
        user = self.env.user
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        return employee.id if employee else False

    def action_join_project(self):
        """Add employee to the project"""
        self.ensure_one()
        if self.project_id and self.employee_id:
            # Add employee to project if not already added
            if self.employee_id not in self.project_id.employee_ids:
                self.project_id.write({
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

