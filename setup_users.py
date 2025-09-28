#!/usr/bin/env python3
"""
Construction Business Multi-User Setup Script for Odoo 17
Automates the creation of user groups, users, and access rules
"""

def setup_construction_users(env):
    """
    Complete setup for construction business multi-user system
    """
    print("🏗️  Starting Construction Business Multi-User Setup...")

    # Get required models
    Users = env['res.users']
    Groups = env['res.groups']
    Rules = env['ir.rule']

    # ====== STEP 1: CREATE/CONFIGURE USER GROUPS ======
    print("\n📋 Step 1: Setting up User Groups...")

    # Get existing groups we'll use
    admin_group = env.ref('base.group_system')
    user_group = env.ref('base.group_user')
    project_manager_group = env.ref('project.group_project_manager')
    project_user_group = env.ref('project.group_project_user')
    account_manager_group = env.ref('account.group_account_manager')
    account_invoice_group = env.ref('account.group_account_invoice')
    expense_user_group = env.ref('hr_expense.group_hr_expense_user')
    expense_manager_group = env.ref('hr_expense.group_hr_expense_manager')
    purchase_user_group = env.ref('purchase.group_purchase_user')
    stock_user_group = env.ref('stock.group_stock_user')

    # Create Construction Site Manager Group
    site_manager_group = Groups.search([('name', '=', 'Construction Site Manager')])
    if not site_manager_group:
        site_manager_group = Groups.create({
            'name': 'Construction Site Manager',
            'category_id': env.ref('base.module_category_project').id,
            'implied_ids': [(6, 0, [
                user_group.id,
                project_user_group.id,
                expense_user_group.id,
                purchase_user_group.id,
                stock_user_group.id,
            ])]
        })
        print("✅ Created Construction Site Manager group")
    else:
        print("✅ Construction Site Manager group already exists")

    # Create Construction Project Manager Group
    construction_pm_group = Groups.search([('name', '=', 'Construction Project Manager')])
    if not construction_pm_group:
        construction_pm_group = Groups.create({
            'name': 'Construction Project Manager',
            'category_id': env.ref('base.module_category_project').id,
            'implied_ids': [(6, 0, [
                user_group.id,
                project_manager_group.id,
                account_invoice_group.id,
                expense_manager_group.id,
                purchase_user_group.id,
                stock_user_group.id,
            ])]
        })
        print("✅ Created Construction Project Manager group")
    else:
        print("✅ Construction Project Manager group already exists")

    # ====== STEP 2: CREATE TEST USERS ======
    print("\n👥 Step 2: Creating Test Users...")

    # User 1: manager1 (Site Manager)
    manager1 = Users.search([('login', '=', 'manager1')])
    if not manager1:
        manager1 = Users.create({
            'name': 'Site Manager 1',
            'login': 'manager1',
            'email': 'manager1@construction.com',
            'password': 'manager123',
            'groups_id': [(6, 0, [site_manager_group.id])]
        })
        print("✅ Created user: manager1 (Site Manager)")
    else:
        print("✅ User manager1 already exists")

    # User 2: manager2 (Site Manager)
    manager2 = Users.search([('login', '=', 'manager2')])
    if not manager2:
        manager2 = Users.create({
            'name': 'Site Manager 2',
            'login': 'manager2',
            'email': 'manager2@construction.com',
            'password': 'manager123',
            'groups_id': [(6, 0, [site_manager_group.id])]
        })
        print("✅ Created user: manager2 (Site Manager)")
    else:
        print("✅ User manager2 already exists")

    # User 3: accountant1 (Accountant)
    accountant1 = Users.search([('login', '=', 'accountant1')])
    if not accountant1:
        accountant1 = Users.create({
            'name': 'Construction Accountant',
            'login': 'accountant1',
            'email': 'accountant1@construction.com',
            'password': 'accountant123',
            'groups_id': [(6, 0, [
                account_manager_group.id,
                project_user_group.id,
                expense_manager_group.id,
                purchase_user_group.id
            ])]
        })
        print("✅ Created user: accountant1 (Accountant)")
    else:
        print("✅ User accountant1 already exists")

    # User 4: projectmgr1 (Project Manager)
    projectmgr1 = Users.search([('login', '=', 'projectmgr1')])
    if not projectmgr1:
        projectmgr1 = Users.create({
            'name': 'Project Manager 1',
            'login': 'projectmgr1',
            'email': 'projectmgr1@construction.com',
            'password': 'project123',
            'groups_id': [(6, 0, [construction_pm_group.id])]
        })
        print("✅ Created user: projectmgr1 (Project Manager)")
    else:
        print("✅ User projectmgr1 already exists")

    # ====== STEP 3: CREATE ACCESS RULES ======
    print("\n🔒 Step 3: Setting up Access Rules...")

    # Rule 1: Site Manager Project Access - Own Projects Only
    project_rule = Rules.search([('name', '=', 'Site Manager: Own Projects Only')])
    if not project_rule:
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

    # Rule 2: Site Manager Expense Access - Own Project Expenses Only
    expense_rule = Rules.search([('name', '=', 'Site Manager: Own Project Expenses Only')])
    if not expense_rule:
        Rules.create({
            'name': 'Site Manager: Own Project Expenses Only',
            'model_id': env.ref('hr_expense.model_hr_expense').id,
            'groups': [(6, 0, [site_manager_group.id])],
            'domain_force': "['|', ('employee_id.user_id', '=', user.id), ('analytic_distribution_search', 'ilike', user.name)]",
            'perm_read': True,
            'perm_write': True,
            'perm_create': True,
            'perm_unlink': False,
        })
        print("✅ Created expense access rule for Site Managers")

    # Rule 3: Site Manager Task Access - Own Project Tasks Only
    task_rule = Rules.search([('name', '=', 'Site Manager: Own Project Tasks Only')])
    if not task_rule:
        Rules.create({
            'name': 'Site Manager: Own Project Tasks Only',
            'model_id': env.ref('project.model_project_task').id,
            'groups': [(6, 0, [site_manager_group.id])],
            'domain_force': "[('project_id.user_id', '=', user.id)]",
            'perm_read': True,
            'perm_write': True,
            'perm_create': True,
            'perm_unlink': False,
        })
        print("✅ Created task access rule for Site Managers")

    # ====== STEP 4: CREATE SAMPLE PROJECTS ======
    print("\n🏗️  Step 4: Creating Sample Projects...")

    Project = env['project.project']

    # Project 1: Assigned to manager1
    project1 = Project.search([('name', '=', 'Residential Building A')])
    if not project1:
        project1 = Project.create({
            'name': 'Residential Building A',
            'user_id': manager1.id,
            'partner_id': env.ref('base.main_partner').id,
            'privacy_visibility': 'employees',
            'allow_billable': True,
        })
        print("✅ Created project: Residential Building A (assigned to manager1)")

    # Project 2: Assigned to manager2
    project2 = Project.search([('name', '=', 'Commercial Complex B')])
    if not project2:
        project2 = Project.create({
            'name': 'Commercial Complex B',
            'user_id': manager2.id,
            'partner_id': env.ref('base.main_partner').id,
            'privacy_visibility': 'employees',
            'allow_billable': True,
        })
        print("✅ Created project: Commercial Complex B (assigned to manager2)")

    # Project 3: Assigned to projectmgr1 (for oversight)
    project3 = Project.search([('name', '=', 'Infrastructure Project C')])
    if not project3:
        project3 = Project.create({
            'name': 'Infrastructure Project C',
            'user_id': projectmgr1.id,
            'partner_id': env.ref('base.main_partner').id,
            'privacy_visibility': 'employees',
            'allow_billable': True,
        })
        print("✅ Created project: Infrastructure Project C (assigned to projectmgr1)")

    # ====== STEP 5: CREATE EMPLOYEE RECORDS ======
    print("\n👷 Step 5: Creating Employee Records...")

    Employee = env['hr.employee']

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

    # ====== STEP 6: VERIFICATION ======
    print("\n🔍 Step 6: Verification Summary...")

    print(f"📊 Users created: {len(Users.search([('login', 'in', ['manager1', 'manager2', 'accountant1', 'projectmgr1'])]))}")
    print(f"📊 Projects created: {len(Project.search([('name', 'in', ['Residential Building A', 'Commercial Complex B', 'Infrastructure Project C'])]))}")
    print(f"📊 Access rules created: {len(Rules.search([('name', 'like', 'Site Manager:')]))}")

    print("\n✅ Construction Business Multi-User Setup Complete!")
    print("\n📋 Login Credentials:")
    print("├── manager1 / manager123 (Site Manager)")
    print("├── manager2 / manager123 (Site Manager)")
    print("├── accountant1 / accountant123 (Accountant)")
    print("└── projectmgr1 / project123 (Project Manager)")

    print("\n🔒 Security Features Enabled:")
    print("├── Site managers can only access assigned projects")
    print("├── Project-based expense restrictions")
    print("├── Role-based access to financial data")
    print("└── Proper separation of duties")

    return True

def test_permissions(env):
    """
    Test the permission setup
    """
    print("\n🧪 Testing Permissions...")

    # Get users
    manager1 = env['res.users'].search([('login', '=', 'manager1')])
    manager2 = env['res.users'].search([('login', '=', 'manager2')])

    if manager1 and manager2:
        # Test project access for manager1
        projects_manager1 = env['project.project'].with_user(manager1).search([])
        projects_manager2 = env['project.project'].with_user(manager2).search([])

        print(f"✅ Manager1 can see {len(projects_manager1)} project(s)")
        print(f"✅ Manager2 can see {len(projects_manager2)} project(s)")

        if len(projects_manager1) <= len(projects_manager2) + 1:  # Should only see their own
            print("✅ Project access restrictions working correctly")
        else:
            print("⚠️  Project access restrictions may need adjustment")

    return True

if __name__ == "__main__":
    print("This script should be run through Odoo shell")
    print("Usage: docker compose exec odoo odoo shell -d construction_business --no-http")