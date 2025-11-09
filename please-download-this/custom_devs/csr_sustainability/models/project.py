# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    is_sustainability = fields.Boolean(string='Sustainability Project', default=False, help='Mark this project as part of the Sustainability app')
    ngo_id = fields.Many2one('csr.ngo', string='NGO', help='NGO associated with this project', index=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees', help='Employees associated with this project')
    completed_by_employee_ids = fields.Many2many('hr.employee', 'project_employee_completion_rel', 'project_id', 'employee_id', 
                                                  string='Completed By', help='Employees who have completed this project')
    xp = fields.Float(string='XP (Experience Points)', default=0.0, help='Experience points that employees can earn by completing this project')
    can_mark_done = fields.Boolean(string='Can Mark Done', compute='_compute_can_mark_done', help='Whether the current employee can mark this project as done')
    project_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], string='Project Status', compute='_compute_project_status', store=True, help='Status of the project based on employee participation')
    
    @api.depends('employee_ids', 'completed_by_employee_ids', 'is_sustainability')
    def _compute_project_status(self):
        """Compute project status based on employee participation"""
        for project in self:
            if not project.is_sustainability:
                project.project_status = False
            elif not project.employee_ids:
                project.project_status = 'not_started'
            elif project.completed_by_employee_ids:
                project.project_status = 'done'
            else:
                project.project_status = 'in_progress'
    
    @api.depends('employee_ids', 'completed_by_employee_ids', 'is_sustainability')
    def _compute_can_mark_done(self):
        """Compute if current employee can mark this project as done"""
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        for project in self:
            if not project.is_sustainability or not employee:
                project.can_mark_done = False
            else:
                # Can mark done if employee is in project and hasn't completed it
                project.can_mark_done = (
                    employee.id in project.employee_ids.ids and 
                    employee.id not in project.completed_by_employee_ids.ids
                )
    
    def action_mark_done(self):
        """Mark this project as done for the current employee and award XP"""
        self.ensure_one()
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        if not employee:
            raise ValueError("No employee record found for the current user")
        
        if employee not in self.employee_ids:
            raise ValueError("You must be a member of this project to mark it as done")
        
        if employee in self.completed_by_employee_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Info',
                    'message': 'You have already marked this project as done.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Add employee to completed list
        self.sudo().write({
            'completed_by_employee_ids': [(4, employee.id)]
        })
        
        # Award XP to employee
        if self.xp > 0:
            employee.sudo().write({
                'sustainability_points': employee.sustainability_points + int(self.xp)
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Project marked as done! You earned {int(self.xp)} XP.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Project marked as done!',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    @api.depends('ngo_id', 'ngo_id.user_id')
    def _compute_ngo_user_id(self):
        """Compute the NGO user ID for record rule filtering"""
        for project in self:
            project.ngo_user_id = project.ngo_id.user_id.id if project.ngo_id and project.ngo_id.user_id else False
    
    ngo_user_id = fields.Many2one('res.users', string='NGO User', compute='_compute_ngo_user_id', store=True, readonly=True, index=True, help='User account of the NGO')
    
    
    @api.model
    def _search_ngo_user_match(self, operator, value):
        """Search for projects where the NGO's user_id matches the current user"""
        if operator != '=' or value != self.env.user.id:
            return []
        # Find all NGOs linked to the current user
        ngos = self.env['csr.ngo'].search([('user_id', '=', self.env.user.id)])
        if not ngos:
            return [('id', '=', False)]  # Return empty result if no NGO found
        return [('ngo_id', 'in', ngos.ids)]
    
    # portal.mixin override
    def _compute_access_url(self):
        super()._compute_access_url()
        for project in self:
            if project.is_sustainability:
                project.access_url = f'/my/projects/{project.id}'
