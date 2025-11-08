# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    is_sustainability = fields.Boolean(string='Sustainability Project', default=False, help='Mark this project as part of the Sustainability app')
    ngo_id = fields.Many2one('csr.ngo', string='NGO', help='NGO associated with this project', index=True)
    
    @api.depends('ngo_id', 'ngo_id.user_id')
    def _compute_ngo_user_id(self):
        """Compute the NGO user ID for record rule filtering"""
        for project in self:
            project.ngo_user_id = project.ngo_id.user_id.id if project.ngo_id and project.ngo_id.user_id else False
    
    ngo_user_id = fields.Many2one('res.users', string='NGO User', compute='_compute_ngo_user_id', store=True, readonly=True, index=True, help='User account of the NGO')
    
    @api.model
    def create(self, vals):
        # Automatically mark projects created by NGO users as sustainability projects
        # and link them to the NGO
        if self.env.user.has_group('csr_sustainability.group_ngo_portal'):
            vals['is_sustainability'] = True
            # Find the NGO linked to the current user
            ngo = self.env['csr.ngo'].search([('user_id', '=', self.env.user.id)], limit=1)
            if ngo:
                vals['ngo_id'] = ngo.id
        return super(ProjectProject, self).create(vals)
    
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
