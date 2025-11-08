# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sustainability_points = fields.Integer(string='Sustainability Points')
    sustainability_category = fields.Selection([
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance'),
    ], string='Sustainability Category')
    difficulty = fields.Selection([
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], string='Difficulty')

    # Add custom fields for Sustainability tasks here
    # Example fields (you can customize these):
    # sustainability_impact = fields.Text(string='Sustainability Impact')
    # target_metric = fields.Char(string='Target Metric')
    # actual_metric = fields.Char(string='Actual Metric')
    # is_sustainability_task = fields.Boolean(string='Sustainability Task', default=True)

