# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal


class ProjectPortal(portal.CustomerPortal):
    _items_per_page = 80

    def _prepare_portal_layout_values(self):
        values = super(ProjectPortal, self)._prepare_portal_layout_values()
        # Add project count and NGO info for portal home - check if user is linked to NGO
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if ngo:
            project_count = request.env['project.project'].sudo().search_count([
                ('is_sustainability', '=', True),
                ('ngo_id', '=', ngo.id)
            ])
            values['project_count'] = project_count
            values['has_ngo'] = True
        else:
            values['has_ngo'] = False
        return values

    def _prepare_home_portal_values(self, counters):
        values = super(ProjectPortal, self)._prepare_home_portal_values(counters)
        # Always compute project_count and has_ngo for NGO users if it's requested or if counters is empty (initial load)
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if ngo:
            values['has_ngo'] = True
            if 'project_count' in counters or not counters:
                values['project_count'] = request.env['project.project'].sudo().search_count([
                    ('is_sustainability', '=', True),
                    ('ngo_id', '=', ngo.id)
                ])
        else:
            values['has_ngo'] = False
        return values
    @http.route(['/my/projects/new'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def portal_my_projects_new(self, **kw):
        """Create a new sustainability project"""
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not ngo:
            return request.redirect('/my/home')

        if request.httprequest.method == 'POST':
            vals = {
                'name': kw.get('name'),
                'description': kw.get('description') or '',
                'date_start': kw.get('date_start') or False,
                'date': kw.get('date') or False,
                'ngo_id': ngo.id,
                'is_sustainability': True,
            }
            # Remove empty values
            vals = {k: v for k, v in vals.items() if v}
            project = request.env['project.project'].sudo().create(vals)
            return request.redirect(f'/my/projects/{project.id}')

        values = {
            'page_name': 'project',
            'default_url': '/my/projects/new',
            'ngo': ngo,
        }
        return request.render("csr_sustainability.portal_project_new", values)

    @http.route(['/my/projects/<int:project_id>/edit'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def portal_my_projects_edit(self, project_id=None, **kw):
        """Edit a sustainability project"""
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not ngo:
            return request.redirect('/my/home')
        
        try:
            project = request.env['project.project'].sudo().browse(project_id)
            if not project.exists():
                return request.redirect('/my/projects')
        except:
            return request.redirect('/my/projects')
        
        # Check access
        if project.ngo_id != ngo or not project.is_sustainability:
            return request.redirect('/my/projects')
        
        if request.httprequest.method == 'POST':
            vals = {
                'name': kw.get('name'),
                'description': kw.get('description') or '',
                'date_start': kw.get('date_start') or False,
                'date': kw.get('date') or False,
            }
            # Remove empty values but keep description
            vals = {k: v for k, v in vals.items() if v is not False or k == 'description'}
            project.write(vals)
            return request.redirect(f'/my/projects/{project.id}')
        
        values = {
            'project': project,
            'page_name': 'project',
            'default_url': '/my/projects/edit',
        }
        return request.render("csr_sustainability.portal_project_edit", values)


    @http.route(['/my/projects', '/my/projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, **kw):
        """Display list of sustainability projects for NGO users"""
        # Check if user is linked to an NGO (more flexible check)
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not ngo:
            # Show a helpful message if NGO is not linked
            values = {
                'page_name': 'project',
                'error_message': 'No NGO account found. Please contact your administrator to link an NGO to your user account.',
            }
            return request.render("csr_sustainability.portal_my_projects", values)
        
        # Check if user has portal access (warn if not)
        if not request.env.user.has_group('base.group_portal'):
            values = {
                'page_name': 'project',
                'error_message': f'Your user account "{request.env.user.login}" is not set up as a portal user. Please contact your administrator to grant portal access and assign you to the "NGO Portal User" group.',
            }
            return request.render("csr_sustainability.portal_my_projects", values)
        
        # Use sudo to bypass record rules for portal users
        Project = request.env['project.project'].sudo()
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
            'ngo': ngo,
            'project_count': project_count,
        }
        
        return request.render("csr_sustainability.portal_my_projects", values)

    @http.route(['/my/projects/<int:project_id>'], type='http', auth="user", website=True)
    def portal_project_page(self, project_id=None, access_token=None, **kw):
        """Display a single sustainability project"""
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
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

