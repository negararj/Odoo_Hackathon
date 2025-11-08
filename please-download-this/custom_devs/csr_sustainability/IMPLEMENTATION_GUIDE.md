# Step-by-Step Implementation Guide

## Overview
This guide walks through implementing all features described in the README.md for the CSR and Sustainability Odoo module.

---

## PART 1: Employee Features

### Step 1: Employee Skills Integration
**Goal:** Employees inherit skills from Odoo's hr.employee model

**Implementation:**
1. Check if `hr_skills` module is available (it's a standard Odoo module)
2. If available, add it to dependencies in `__manifest__.py`
3. The skills are already available through `hr.employee.skill` model
4. Add a computed field or related field to display skills in employee views

**Files to modify:**
- `__manifest__.py` - Add `'hr_skills'` to depends if available
- `models/employee.py` - Add computed field for skills display
- `views/employee_views.xml` - Display skills in form view

---

### Step 2: Employee Project Selection/Joining
**Goal:** Employees can choose/join projects from NGOs

**Implementation:**
1. Add a Many2many field `employee_ids` to `project.project` to track which employees joined
2. Add a button/wizard for employees to join projects
3. Create a view showing available sustainability projects
4. Add a method to allow employees to join projects

**Files to create/modify:**
- `models/project.py` - Add `employee_ids` Many2many field
- `wizards/__init__.py` - New file
- `wizards/join_project_wizard.py` - Wizard for joining projects
- `views/project_views.xml` - Add employee_ids field and join button
- `views/join_project_wizard_views.xml` - Wizard form view

---

### Step 3: Sustainability Points Award System
**Goal:** Employees get sustainability_points when completing tasks

**Implementation:**
1. Add a method to automatically award points when task is completed
2. Override task state change to award points
3. Update employee's total sustainability_points
4. Add tracking/logging for point awards

**Files to modify:**
- `models/task.py` - Add method to award points on completion
- `models/employee.py` - Add method to update total points
- `data/` - Optional: Add automation rules

**Logic:**
```python
# When task.state changes to 'done' or '1_done'
# Award sustainability_points from task to assigned employees
# Update employee.sustainability_points += task.sustainability_points
```

---

### Step 4: Activity Exchange System
**Goal:** Employees can exchange sustainability_points for activities (planting trees, donating, etc.)

**Implementation:**
1. Create new model `csr.activity` with fields:
   - name (Char)
   - activity_type (Selection: 'plant_tree', 'donate', 'volunteer', etc.)
   - points_cost (Integer) - How many points needed
   - o2_reward (Float) - O2 currency earned
   - description (Text)
   - active (Boolean)

2. Create new model `csr.activity.participation` (Many2one to activity and employee):
   - activity_id (Many2one to csr.activity)
   - employee_id (Many2one to hr.employee)
   - participation_date (Date)
   - points_spent (Integer)
   - o2_earned (Float)
   - state (Selection: 'pending', 'completed', 'verified')

3. Create wizard for employees to exchange points for activities
4. Add validation to ensure employee has enough points
5. Deduct points and award O2 when activity is completed

**Files to create:**
- `models/activity.py` - csr.activity model
- `models/activity_participation.py` - csr.activity.participation model
- `wizards/exchange_points_wizard.py` - Wizard for exchanging points
- `views/activity_views.xml` - Views for activities
- `views/activity_participation_views.xml` - Views for participations
- `views/exchange_points_wizard_views.xml` - Wizard view
- `security/ir.model.access.csv` - Add access rights
- `views/menu.xml` - Add menu items

**Files to modify:**
- `models/__init__.py` - Import new models
- `models/employee.py` - Add One2many to participations
- `views/employee_views.xml` - Show participations

---

### Step 5: O2 Currency System
**Goal:** Employees earn O2 currency from activities

**Implementation:**
1. The `money_O2` field already exists in employee model
2. Update O2 when activity participation is verified/completed
3. Add currency configuration (if needed)
4. Add O2 transaction history

**Files to modify:**
- `models/activity_participation.py` - Update employee O2 on completion
- `models/employee.py` - Add method to update O2
- `views/employee_views.xml` - Display O2 prominently

---

### Step 6: Employee Leaderboard
**Goal:** Leaderboard sorted by O2 currency

**Implementation:**
1. Create a new action/view for leaderboard
2. Use kanban or list view sorted by money_O2 descending
3. Add ranking numbers
4. Add filters (by department, by badge, etc.)

**Files to create:**
- `views/leaderboard_views.xml` - Leaderboard views
- `views/menu.xml` - Add leaderboard menu item

**Files to modify:**
- `models/employee.py` - Add computed field for rank (optional)

---

### Step 7: Employee Project View
**Goal:** Employees can see their projects (pending and done)

**Implementation:**
1. Use existing Odoo project views
2. Filter projects where employee is in `employee_ids`
3. Add filters for project state (pending/done)
4. Show tasks assigned to employee

**Files to modify:**
- `views/project_views.xml` - Add employee-specific filters
- `views/menu.xml` - Add "My Projects" menu for employees

---

## PART 2: NGO Features

### Step 8: NGO Portal User Setup
**Goal:** NGOs are portal users (Already implemented ✓)

**Status:** Already done - NGOs have portal user access

---

### Step 9: NGO Project Creation
**Goal:** NGOs can add projects through portal

**Implementation:**
1. Portal views already exist for project creation
2. Ensure NGOs can create projects via portal
3. Add form view for project creation in portal
4. Auto-set `is_sustainability=True` and `ngo_id` (already done in create method)

**Files to modify:**
- `controllers/portal.py` - Add route for project creation form
- `views/portal_project_templates.xml` - Add "Create Project" button and form

---

### Step 10: NGO Activity Management
**Goal:** NGOs can add and manage activities

**Implementation:**
1. Add portal access for NGOs to create activities
2. Create portal views for activity management
3. Add CRUD operations (Create, Read, Update, Delete) for activities
4. Link activities to NGO (optional: add ngo_id to activity model)

**Files to create:**
- `views/portal_activity_templates.xml` - Portal templates for activities
- `controllers/portal.py` - Add routes for activity management

**Files to modify:**
- `models/activity.py` - Add ngo_id field (optional)
- `security/ir_rule.xml` - Add rules for NGO activity access

---

### Step 11: NGO Project & Activity Status View
**Goal:** NGOs can see projects and activities (done/pending)

**Implementation:**
1. Add filters in portal views for project state
2. Add filters for activity participation state
3. Create dashboard showing statistics
4. Show pending vs completed counts

**Files to modify:**
- `views/portal_project_templates.xml` - Add status filters
- `controllers/portal.py` - Add dashboard route with statistics
- `views/portal_activity_templates.xml` - Add status filters

---

## PART 3: Additional Features

### Step 12: Notifications & Workflow
**Goal:** Notify employees when points are awarded, activities are available, etc.

**Implementation:**
1. Add mail templates for notifications
2. Send emails when:
   - Employee completes a task (points awarded)
   - Employee joins a project
   - New activity is available
   - Activity participation is verified

**Files to create:**
- `data/mail_templates.xml` - Email templates

---

### Step 13: Reporting & Analytics
**Goal:** Reports for sustainability metrics

**Implementation:**
1. Create reports for:
   - Employee sustainability points over time
   - O2 currency distribution
   - Activity participation statistics
   - Project completion rates
   - NGO project statistics

**Files to create:**
- `reports/sustainability_reports.xml` - Report definitions

---

## Implementation Order Recommendation

**Phase 1 - Core Functionality:**
1. Step 4: Activity Exchange System (most complex, foundation for others)
2. Step 3: Sustainability Points Award System
3. Step 5: O2 Currency System
4. Step 2: Employee Project Selection

**Phase 2 - Employee Features:**
5. Step 6: Employee Leaderboard
6. Step 7: Employee Project View
7. Step 1: Employee Skills Integration

**Phase 3 - NGO Features:**
8. Step 9: NGO Project Creation (enhance existing)
9. Step 10: NGO Activity Management
10. Step 11: NGO Project & Activity Status View

**Phase 4 - Polish:**
11. Step 12: Notifications & Workflow
12. Step 13: Reporting & Analytics

---

## Technical Notes

1. **Skills Module:** Check if `hr_skills` is installed. If not, you may need to create a simple skills field or use tags.

2. **Points System:** Consider adding a transaction log model to track all point awards/deductions for audit purposes.

3. **O2 Currency:** You may want to add a currency configuration model if O2 needs exchange rates or conversion rules.

4. **Security:** Ensure proper access rights for all new models, especially for portal users.

5. **Performance:** For leaderboard, consider using stored computed fields or SQL views for better performance with many employees.

---

## Testing Checklist

- [ ] Employee can join a project
- [ ] Employee receives points when completing tasks
- [ ] Employee can exchange points for activities
- [ ] Employee receives O2 when activity is completed
- [ ] Leaderboard displays correctly sorted by O2
- [ ] Employee can view their projects
- [ ] NGO can create projects via portal
- [ ] NGO can create activities via portal
- [ ] NGO can view project/activity status
- [ ] All security rules work correctly
- [ ] Portal views are accessible and functional

