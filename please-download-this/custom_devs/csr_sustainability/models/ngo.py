# -*- coding: utf-8 -*-
from odoo import api, fields, models


class NGO(models.Model):
    _name = 'csr.ngo'
    _description = 'NGO (Non-Governmental Organization)'
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(string='NGO Name', required=True)
    user_id = fields.Many2one('res.users', string='Login User', required=True, help='User account for this NGO to log in and create projects')
    project_ids = fields.One2many('project.project', 'ngo_id', string='Projects')
    project_count = fields.Integer(string='Project Count', compute='_compute_project_count')
    active = fields.Boolean(string='Active', default=True)
    
    @api.depends('project_ids')
    def _compute_project_count(self):
        for ngo in self:
            ngo.project_count = len(ngo.project_ids)

