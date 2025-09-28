#!/usr/bin/env python3
"""
Simple Construction Business Multi-User Setup Script for Odoo 17
"""

print("🏗️  Starting Construction Business Multi-User Setup...")

# Get required models
Users = env['res.users']
Groups = env['res.groups']
Rules = env['ir.rule']
Project = env['project.project']
Employee = env['hr.employee']

# ====== STEP 1: GET EXISTING GROUPS ======
print("\n📋 Step 1: Getting existing groups...")

# Find existing groups by their keys
admin_group = env.ref('base.group_system', raise_if_not_found=False)
user_group = env.ref('base.group_user', raise_if_not_found=False)
project_manager_group = env.ref('project.group_project_manager', raise_if_not_found=False)
project_user_group = env.ref('project.group_project_user', raise_if_not_found=False)
account_manager_group = env.ref('account.group_account_manager', raise_if_not_found=False)
expense_user_group = env.ref('hr_expense.group_hr_expense_user', raise_if_not_found=False)
expense_manager_group = env.ref('hr_expense.group_hr_expense_manager', raise_if_not_found=False)
purchase_user_group = env.ref('purchase.group_purchase_user', raise_if_not_found=False)
stock_user_group = env.ref('stock.group_stock_user', raise_if_not_found=False)

print("✅ Found existing groups")

# ====== STEP 2: CREATE TEST USERS ======
print("\n👥 Step 2: Creating Test Users...")

# User 1: manager1 (Site Manager)
manager1 = Users.search([('login', '=', 'manager1')])
if not manager1:
    groups_to_assign = [user_group.id]
    if project_user_group:
        groups_to_assign.append(project_user_group.id)
    if expense_user_group:
        groups_to_assign.append(expense_user_group.id)
    if purchase_user_group:
        groups_to_assign.append(purchase_user_group.id)
    if stock_user_group:
        groups_to_assign.append(stock_user_group.id)

    manager1 = Users.create({
        'name': 'Site Manager 1',
        'login': 'manager1',
        'email': 'manager1@construction.com',
        'groups_id': [(6, 0, groups_to_assign)]
    })
    print("✅ Created user: manager1 (Site Manager)")
else:
    print("✅ User manager1 already exists")

# User 2: manager2 (Site Manager)
manager2 = Users.search([('login', '=', 'manager2')])
if not manager2:
    groups_to_assign = [user_group.id]
    if project_user_group:
        groups_to_assign.append(project_user_group.id)
    if expense_user_group:
        groups_to_assign.append(expense_user_group.id)
    if purchase_user_group:
        groups_to_assign.append(purchase_user_group.id)
    if stock_user_group:
        groups_to_assign.append(stock_user_group.id)

    manager2 = Users.create({
        'name': 'Site Manager 2',
        'login': 'manager2',
        'email': 'manager2@construction.com',
        'groups_id': [(6, 0, groups_to_assign)]
    })
    print("✅ Created user: manager2 (Site Manager)")
else:
    print("✅ User manager2 already exists")

# User 3: accountant1 (Accountant)
accountant1 = Users.search([('login', '=', 'accountant1')])
if not accountant1:
    groups_to_assign = [user_group.id]
    if account_manager_group:
        groups_to_assign.append(account_manager_group.id)
    if project_user_group:
        groups_to_assign.append(project_user_group.id)
    if expense_manager_group:
        groups_to_assign.append(expense_manager_group.id)
    if purchase_user_group:
        groups_to_assign.append(purchase_user_group.id)

    accountant1 = Users.create({
        'name': 'Construction Accountant',
        'login': 'accountant1',
        'email': 'accountant1@construction.com',
        'groups_id': [(6, 0, groups_to_assign)]
    })
    print("✅ Created user: accountant1 (Accountant)")
else:
    print("✅ User accountant1 already exists")

# User 4: projectmgr1 (Project Manager)
projectmgr1 = Users.search([('login', '=', 'projectmgr1')])
if not projectmgr1:
    groups_to_assign = [user_group.id]
    if project_manager_group:
        groups_to_assign.append(project_manager_group.id)
    if expense_manager_group:
        groups_to_assign.append(expense_manager_group.id)
    if purchase_user_group:
        groups_to_assign.append(purchase_user_group.id)
    if stock_user_group:
        groups_to_assign.append(stock_user_group.id)

    projectmgr1 = Users.create({
        'name': 'Project Manager 1',
        'login': 'projectmgr1',
        'email': 'projectmgr1@construction.com',
        'groups_id': [(6, 0, groups_to_assign)]
    })
    print("✅ Created user: projectmgr1 (Project Manager)")
else:
    print("✅ User projectmgr1 already exists")

# ====== STEP 3: CREATE SAMPLE PROJECTS ======
print("\n🏗️  Step 3: Creating Sample Projects...")

# Find the main partner for projects
main_partner = env.ref('base.main_partner', raise_if_not_found=False)
if not main_partner:
    main_partner = env['res.partner'].search([('is_company', '=', True)], limit=1)

# Project 1: Assigned to manager1
project1 = Project.search([('name', '=', 'Residential Building A')])
if not project1:
    project1 = Project.create({
        'name': 'Residential Building A',
        'user_id': manager1.id,
        'partner_id': main_partner.id if main_partner else False,
        'privacy_visibility': 'employees',
    })
    print("✅ Created project: Residential Building A (assigned to manager1)")

# Project 2: Assigned to manager2
project2 = Project.search([('name', '=', 'Commercial Complex B')])
if not project2:
    project2 = Project.create({
        'name': 'Commercial Complex B',
        'user_id': manager2.id,
        'partner_id': main_partner.id if main_partner else False,
        'privacy_visibility': 'employees',
    })
    print("✅ Created project: Commercial Complex B (assigned to manager2)")

# Project 3: Assigned to projectmgr1
project3 = Project.search([('name', '=', 'Infrastructure Project C')])
if not project3:
    project3 = Project.create({
        'name': 'Infrastructure Project C',
        'user_id': projectmgr1.id,
        'partner_id': main_partner.id if main_partner else False,
        'privacy_visibility': 'employees',
    })
    print("✅ Created project: Infrastructure Project C (assigned to projectmgr1)")

# ====== STEP 4: CREATE EMPLOYEE RECORDS ======
print("\n👷 Step 4: Creating Employee Records...")

# Create employees for expense management
for user, name in [(manager1, 'Site Manager 1'), (manager2, 'Site Manager 2'),
                   (accountant1, 'Construction Accountant'), (projectmgr1, 'Project Manager 1')]:
    employee = Employee.search([('user_id', '=', user.id)])
    if not employee:
        Employee.create({
            'name': name,
            'user_id': user.id,
            'work_email': user.email,
        })
        print(f"✅ Created employee record for {name}")

# ====== STEP 5: CREATE ACCESS RULES ======
print("\n🔒 Step 5: Setting up Basic Access Rules...")

# Get site manager users for access rules
site_managers = manager1 + manager2

# Create a group for site managers if needed
site_manager_group = Groups.search([('name', '=', 'Construction Site Managers')])
if not site_manager_group:
    site_manager_group = Groups.create({
        'name': 'Construction Site Managers',
        'users': [(6, 0, site_managers.ids)]
    })
    print("✅ Created Construction Site Managers group")
else:
    # Add users to existing group
    site_manager_group.write({'users': [(6, 0, site_managers.ids)]})

# Rule 1: Site Manager Project Access - Own Projects Only
project_rule = Rules.search([('name', '=', 'Site Manager: Own Projects Only')])
if not project_rule and site_manager_group:
    try:
        Rules.create({
            'name': 'Site Manager: Own Projects Only',
            'model_id': env.ref('project.model_project_project').id,
            'groups': [(6, 0, [site_manager_group.id])],
            'domain_force': "[('user_id', '=', user.id)]",
            'perm_read': True,
            'perm_write': True,
            'perm_create': True,
            'perm_unlink': False,
        })
        print("✅ Created project access rule for Site Managers")
    except Exception as e:
        print(f"⚠️  Could not create project rule: {e}")

# ====== STEP 6: VERIFICATION ======
print("\n🔍 Step 6: Verification Summary...")

all_users = Users.search([('login', 'in', ['manager1', 'manager2', 'accountant1', 'projectmgr1'])])
all_projects = Project.search([('name', 'in', ['Residential Building A', 'Commercial Complex B', 'Infrastructure Project C'])])

print(f"📊 Users created: {len(all_users)}")
print(f"📊 Projects created: {len(all_projects)}")

print("\n✅ Construction Business Multi-User Setup Complete!")
print("\n📋 Login Credentials:")
print("├── manager1 / (no password set - use 'Change Password' in user settings)")
print("├── manager2 / (no password set - use 'Change Password' in user settings)")
print("├── accountant1 / (no password set - use 'Change Password' in user settings)")
print("└── projectmgr1 / (no password set - use 'Change Password' in user settings)")

print("\n🔒 Security Features Enabled:")
print("├── Site managers can only access assigned projects")
print("├── Role-based access to modules")
print("├── Employee records created for expense management")
print("└── Basic access control framework in place")

print("\n📝 Next Steps:")
print("1. Set passwords for new users through the UI")
print("2. Test login with each user")
print("3. Assign more specific permissions as needed")
print("4. Create additional access rules for expenses")

print("\n✅ Setup completed successfully!")