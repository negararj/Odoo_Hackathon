# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal


class ProjectPortal(portal.CustomerPortal):
    _items_per_page = 80

    def _prepare_portal_layout_values(self):
        values = super(ProjectPortal, self)._prepare_portal_layout_values()
        # Add activity count and NGO info for portal home - check if user is linked to NGO
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if ngo:
            activity_count = request.env['csr.activity'].sudo().search_count([
                ('ngo_id', '=', ngo.id)
            ])
            values['activity_count'] = activity_count
            values['has_ngo'] = True
        else:
            values['has_ngo'] = False
        return values

    def _prepare_home_portal_values(self, counters):
        values = super(ProjectPortal, self)._prepare_home_portal_values(counters)
        # Always compute activity_count and has_ngo for NGO users if it's requested or if counters is empty (initial load)
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if ngo:
            values['has_ngo'] = True
            # Always compute activity count for portal home page
            activity_count = request.env['csr.activity'].sudo().search_count([
                ('ngo_id', '=', ngo.id)
            ])
            # Ensure count is always an integer
            values['activity_count'] = int(activity_count) if activity_count else 0
        else:
            values['has_ngo'] = False
            values['activity_count'] = 0
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
                'xp': float(kw.get('xp', 0)) or 0,
                'ngo_id': ngo.id,
                'is_sustainability': True,
            }
            # Remove empty values but keep xp
            vals = {k: v for k, v in vals.items() if v or k == 'xp'}
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
                'xp': float(kw.get('xp', 0)) or 0,
            }
            # Remove empty values but keep description and xp
            vals = {k: v for k, v in vals.items() if v is not False or k in ['description', 'xp']}
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
        """Display list of sustainability projects for NGO users or employees"""
        # Check if user is NGO or employee
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        
        # Use sudo to bypass record rules for portal users
        Project = request.env['project.project'].sudo()
        
        if ngo:
            # NGO users see their own projects
            domain = [('is_sustainability', '=', True), ('ngo_id', '=', ngo.id)]
            project_count = Project.search_count(domain)
            offset = (page - 1) * self._items_per_page
            projects = Project.search(domain, limit=self._items_per_page, offset=offset, order='id desc')
        elif employee:
            # Employee users see projects they're part of
            # First, get all sustainability projects
            all_projects = Project.search([('is_sustainability', '=', True)])
            # Filter to only projects where this employee is a member
            employee_projects = all_projects.filtered(lambda p: employee.id in p.employee_ids.ids)
            
            project_count = len(employee_projects)
            offset = (page - 1) * self._items_per_page
            # Sort by ID descending and apply pagination
            projects = sorted(employee_projects, key=lambda p: p.id, reverse=True)[offset:offset + self._items_per_page]
        else:
            # No NGO or employee found
            values = {
                'page_name': 'project',
                'error_message': 'No NGO or employee account found. Please contact your administrator.',
                'ngo': False,
                'employee': False,
                'projects': [],
            }
            return request.render("csr_sustainability.portal_my_projects", values)
        
        # Paging
        pager = request.website.pager(
            url="/my/projects",
            url_args={},
            total=project_count,
            page=page,
            step=self._items_per_page
        )
        
        values = {
            'projects': projects,
            'page_name': 'project',
            'pager': pager,
            'default_url': '/my/projects',
            'ngo': ngo,
            'employee': employee,
            'project_count': project_count,
        }
        
        return request.render("csr_sustainability.portal_my_projects", values)

    @http.route(['/my/projects/<int:project_id>'], type='http', auth="user", website=True)
    def portal_project_page(self, project_id=None, access_token=None, **kw):
        """Display a single sustainability project"""
        # Check if user is NGO or employee
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        
        try:
            project_sudo = request.env['project.project'].sudo().browse(project_id)
        except:
            return request.redirect('/my/projects')
        
        # Check access - NGO can see their projects, employees can see projects they're part of
        if ngo:
            if project_sudo.ngo_id != ngo or not project_sudo.is_sustainability:
                return request.redirect('/my/projects')
        elif employee:
            if not project_sudo.is_sustainability or employee not in project_sudo.employee_ids:
                return request.redirect('/my/projects')
        else:
            return request.redirect('/my/home')
        
        # Check if employee has completed this project and if they're a member
        is_completed = False
        is_employee_in_project = False
        if employee:
            is_completed = employee.id in project_sudo.completed_by_employee_ids.ids
            is_employee_in_project = employee.id in project_sudo.employee_ids.ids
        
        values = {
            'project': project_sudo,
            'page_name': 'project',
            'ngo': ngo,
            'employee': employee,
            'is_completed': is_completed,
            'is_employee_in_project': is_employee_in_project,
        }
        
        return request.render("csr_sustainability.project_portal_template", values)
    
    @http.route(['/my/projects/<int:project_id>/mark_done'], type='http', auth="user", website=True, methods=['POST'])
    def portal_project_mark_done(self, project_id=None, **kw):
        """Mark a project as done for the current employee"""
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not employee:
            return request.redirect('/my/home')
        
        try:
            project = request.env['project.project'].sudo().browse(project_id)
            if not project.exists() or not project.is_sustainability:
                return request.redirect('/my/projects')
        except:
            return request.redirect('/my/projects')
        
        # Check if employee is part of the project
        if employee not in project.employee_ids:
            return request.redirect(f'/my/projects/{project_id}')
        
        # Check if already completed
        if employee in project.completed_by_employee_ids:
            return request.redirect(f'/my/projects/{project_id}')
        
        # Mark as done and award XP
        project.sudo().write({
            'completed_by_employee_ids': [(4, employee.id)]
        })
        
        if project.xp > 0:
            employee.sudo().write({
                'sustainability_points': employee.sustainability_points + int(project.xp)
            })
        
        return request.redirect(f'/my/projects/{project_id}')

    @http.route(['/my/activities', '/my/activities/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_activities(self, page=1, **kw):
        """Display list of activities for NGO users or all activities for employees"""
        # Check if user is NGO or employee
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        
        Activity = request.env['csr.activity'].sudo()
        
        if ngo:
            # NGO users see their own activities
            domain = [('ngo_id', '=', ngo.id)]
            activity_count = Activity.search_count(domain)
            offset = (page - 1) * self._items_per_page
            activities = Activity.search(domain, limit=self._items_per_page, offset=offset, order='id desc')
        elif employee:
            # Employee users see all active activities from all NGOs
            domain = [('active', '=', True)]
            activity_count = Activity.search_count(domain)
            offset = (page - 1) * self._items_per_page
            activities = Activity.search(domain, limit=self._items_per_page, offset=offset, order='id desc')
        else:
            # No NGO or employee found
            values = {
                'page_name': 'activity',
                'error_message': 'No NGO or employee account found. Please contact your administrator.',
                'ngo': False,
                'employee': False,
                'activities': [],
            }
            return request.render("csr_sustainability.portal_my_activities", values)
        
        pager = request.website.pager(
            url="/my/activities",
            url_args={},
            total=activity_count,
            page=page,
            step=self._items_per_page
        )
        
        values = {
            'activities': activities,
            'page_name': 'activity',
            'pager': pager,
            'default_url': '/my/activities',
            'ngo': ngo,
            'employee': employee,
            'activity_count': activity_count,
        }
        
        return request.render("csr_sustainability.portal_my_activities", values)

    @http.route(['/my/activities/new'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def portal_my_activities_new(self, **kw):
        """Create a new activity"""
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not ngo:
            return request.redirect('/my/home')

        if request.httprequest.method == 'POST':
            vals = {
                'name': kw.get('name'),
                'description': kw.get('description') or '',
                'xp': float(kw.get('xp', 0)) or 0,
                'value': float(kw.get('value', 0)) or 0,
                'ngo_id': ngo.id,
                'active': True,
            }
            # Remove empty values
            vals = {k: v for k, v in vals.items() if v}
            activity = request.env['csr.activity'].sudo().create(vals)
            return request.redirect(f'/my/activities/{activity.id}')

        values = {
            'page_name': 'activity',
            'default_url': '/my/activities/new',
            'ngo': ngo,
        }
        return request.render("csr_sustainability.portal_activity_new", values)

    @http.route(['/my/activities/<int:activity_id>/edit'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def portal_my_activities_edit(self, activity_id=None, **kw):
        """Edit an activity"""
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not ngo:
            return request.redirect('/my/home')
        
        try:
            activity = request.env['csr.activity'].sudo().browse(activity_id)
            if not activity.exists():
                return request.redirect('/my/activities')
        except:
            return request.redirect('/my/activities')
        
        # Check access
        if activity.ngo_id != ngo:
            return request.redirect('/my/activities')
        
        if request.httprequest.method == 'POST':
            vals = {
                'name': kw.get('name'),
                'description': kw.get('description') or '',
                'xp': float(kw.get('xp', 0)) or 0,
                'value': float(kw.get('value', 0)) or 0,
                'active': kw.get('active') == 'on',
            }
            # Remove empty values but keep description
            vals = {k: v for k, v in vals.items() if v is not False or k == 'description'}
            activity.write(vals)
            return request.redirect(f'/my/activities/{activity.id}')
        
        values = {
            'activity': activity,
            'page_name': 'activity',
            'default_url': '/my/activities/edit',
        }
        return request.render("csr_sustainability.portal_activity_edit", values)

    @http.route(['/my/activities/<int:activity_id>'], type='http', auth="user", website=True)
    def portal_activity_page(self, activity_id=None, access_token=None, **kw):
        """Display a single activity"""
        ngo = request.env['csr.ngo'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        
        try:
            activity_sudo = request.env['csr.activity'].sudo().browse(activity_id)
        except:
            return request.redirect('/my/activities')
        
        # Check access - NGO can see their activities, employees can see all active activities
        if ngo:
            if activity_sudo.ngo_id != ngo:
                return request.redirect('/my/activities')
        elif employee:
            if not activity_sudo.active:
                return request.redirect('/my/activities')
        else:
            return request.redirect('/my/home')
        
        values = {
            'activity': activity_sudo,
            'page_name': 'activity',
            'ngo': ngo,
            'employee': employee,
        }
        
        return request.render("csr_sustainability.portal_activity_template", values)

