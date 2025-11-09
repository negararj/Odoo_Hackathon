# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CSRActivity(models.Model):
    _name = 'csr.activity'
    _description = 'CSR Activity'
    _inherit = ['portal.mixin']
    _order = 'name'
    
    name = fields.Char(string='Activity Name', required=True)
    description = fields.Text(string='Description')
    ngo_id = fields.Many2one('csr.ngo', string='NGO', required=True, ondelete='cascade', index=True)
    xp = fields.Float(string='XP (Price)', required=True, help='Amount of XP employees need to pay to purchase this activity')
    value = fields.Float(string='O2 Value', required=True, help='Amount of O2 employees receive when purchasing this activity')
    active = fields.Boolean(string='Active', default=True)
    purchase_ids = fields.One2many('csr.activity.purchase', 'activity_id', string='Purchases')
    purchase_count = fields.Integer(string='Purchase Count', compute='_compute_purchase_count')
    
    @api.depends('purchase_ids')
    def _compute_purchase_count(self):
        for activity in self:
            activity.purchase_count = len(activity.purchase_ids)
    
    def _compute_access_url(self):
        super()._compute_access_url()
        for activity in self:
            activity.access_url = f'/my/activities/{activity.id}'


class CSRActivityPurchase(models.Model):
    _name = 'csr.activity.purchase'
    _description = 'CSR Activity Purchase'
    _order = 'purchase_date desc'
    
    activity_id = fields.Many2one('csr.activity', string='Activity', required=True, ondelete='cascade', index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade', index=True)
    purchase_date = fields.Datetime(string='Purchase Date', required=True, default=fields.Datetime.now)
    xp_paid = fields.Float(string='XP Paid', required=True)
    o2_received = fields.Float(string='O2 Received', required=True)
    ngo_id = fields.Many2one('csr.ngo', string='NGO', related='activity_id.ngo_id', store=True, readonly=True)

