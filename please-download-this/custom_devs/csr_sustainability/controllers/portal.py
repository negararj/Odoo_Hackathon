# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal


class ProjectPortal(portal.CustomerPortal):
    _items_per_page = 80

    def _prepare_portal_layout_values(self):
        values = super(ProjectPortal, self)._prepare_portal_layout_values()
        # Add project count for portal home
        if request.env.user.has_group('csr_sustainability.group_ngo_portal'):
            ngo = request.env['csr.ngo'].search([('user_id', '=', request.env.user.id)], limit=1)
            if ngo:
                project_count = request.env['project.project'].search_count([
                    ('is_sustainability', '=', True),
                    ('ngo_id', '=', ngo.id)
                ])
                values['project_count'] = project_count
        return values

    def _prepare_home_portal_values(self, counters):
        values = super(ProjectPortal, self)._prepare_home_portal_values(counters)
        # Always compute project_count for NGO users if it's requested or if counters is empty (initial load)
        if 'project_count' in counters or not counters:
            if request.env.user.has_group('csr_sustainability.group_ngo_portal'):
                ngo = request.env['csr.ngo'].search([('user_id', '=', request.env.user.id)], limit=1)
                if ngo:
                    values['project_count'] = request.env['project.project'].search_count([
                        ('is_sustainability', '=', True),
                        ('ngo_id', '=', ngo.id)
                    ])
        return values

    @http.route(['/my/projects', '/my/projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, **kw):
        """Display list of sustainability projects for NGO users"""
        if not request.env.user.has_group('csr_sustainability.group_ngo_portal'):
            return request.redirect('/my/home')
        
        ngo = request.env['csr.ngo'].search([('user_id', '=', request.env.user.id)], limit=1)
        if not ngo:
            return request.redirect('/my/home')
        
        Project = request.env['project.project']
        domain = [('is_sustainability', '=', True), ('ngo_id', '=', ngo.id)]
        
        # Count projects
        project_count = Project.search_count(domain)
        
        # Paging
        pager = request.website.pager(
            url="/my/projects",
            url_args={},
            total=project_count,
            page=page,
            step=self._items_per_page
        )
        
        # Get projects
        projects = Project.search(domain, limit=self._items_per_page, offset=pager['offset'], order='id desc')
        
        values = {
            'projects': projects,
            'page_name': 'project',
            'pager': pager,
            'default_url': '/my/projects',
        }
        
        return request.render("csr_sustainability.portal_my_projects", values)

    @http.route(['/my/projects/<int:project_id>'], type='http', auth="user", website=True)
    def portal_project_page(self, project_id=None, access_token=None, **kw):
        """Display a single sustainability project"""
        if not request.env.user.has_group('csr_sustainability.group_ngo_portal'):
            return request.redirect('/my/home')
        
        ngo = request.env['csr.ngo'].search([('user_id', '=', request.env.user.id)], limit=1)
        if not ngo:
            return request.redirect('/my/home')
        
        try:
            project_sudo = request.env['project.project'].sudo().browse(project_id)
        except:
            return request.redirect('/my/projects')
        
        # Check access
        if project_sudo.ngo_id != ngo or not project_sudo.is_sustainability:
            return request.redirect('/my/projects')
        
        values = {
            'project': project_sudo,
            'page_name': 'project',
        }
        
        return request.render("csr_sustainability.project_portal_template", values)

