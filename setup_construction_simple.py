#!/usr/bin/env python3
"""
Simplified Construction Project Setup Script for Odoo 17
"""

print("🏗️  Starting Construction Project Structure Setup...")

# Get required models
Project = env['project.project']
ProjectStage = env['project.project.stage']
Task = env['project.task']
AnalyticAccount = env['account.analytic.account']
AnalyticGroup = env['account.analytic.group']
ProductCategory = env['product.category']
Users = env['res.users']

# ====== STEP 1: CREATE PROJECT STAGES ======
print("\n📋 Step 1: Creating Construction Project Stages...")

construction_stages = [
    {'name': 'Planning & Design', 'sequence': 1, 'fold': False},
    {'name': 'Site Preparation', 'sequence': 2, 'fold': False},
    {'name': 'Foundation', 'sequence': 3, 'fold': False},
    {'name': 'Structure & Framing', 'sequence': 4, 'fold': False},
    {'name': 'MEP (Mechanical, Electrical, Plumbing)', 'sequence': 5, 'fold': False},
    {'name': 'Finishing', 'sequence': 6, 'fold': False},
    {'name': 'Final Inspection', 'sequence': 7, 'fold': False},
    {'name': 'Complete', 'sequence': 8, 'fold': True},
]

created_stages = []
for stage_data in construction_stages:
    existing_stage = ProjectStage.search([('name', '=', stage_data['name'])])
    if not existing_stage:
        stage = ProjectStage.create(stage_data)
        created_stages.append(stage)
        print(f"✅ Created stage: {stage_data['name']}")
    else:
        created_stages.append(existing_stage)
        print(f"✅ Stage already exists: {stage_data['name']}")

# ====== STEP 2: CREATE ANALYTIC GROUPS FOR EXPENSE TRACKING ======
print("\n💰 Step 2: Creating Analytic Groups for Expense Tracking...")

# Main Construction group
main_group = AnalyticGroup.search([('name', '=', 'Construction Projects')])
if not main_group:
    main_group = AnalyticGroup.create({
        'name': 'Construction Projects',
        'description': 'Main group for all construction project tracking'
    })
    print("✅ Created main analytic group: Construction Projects")

# Expense category groups
expense_groups = [
    {'name': 'Materials', 'parent_id': main_group.id},
    {'name': 'Labor', 'parent_id': main_group.id},
    {'name': 'Equipment', 'parent_id': main_group.id},
    {'name': 'Overhead', 'parent_id': main_group.id},
    {'name': 'Permits & Fees', 'parent_id': main_group.id},
]

created_expense_groups = []
for group_data in expense_groups:
    existing_group = AnalyticGroup.search([('name', '=', group_data['name']), ('parent_id', '=', main_group.id)])
    if not existing_group:
        group = AnalyticGroup.create(group_data)
        created_expense_groups.append(group)
        print(f"✅ Created expense group: {group_data['name']}")
    else:
        created_expense_groups.append(existing_group)
        print(f"✅ Expense group already exists: {group_data['name']}")

# ====== STEP 3: CREATE EXPENSE PRODUCT CATEGORIES ======
print("\n🛠️  Step 3: Creating Expense Product Categories...")

expense_categories = [
    {
        'name': 'Construction Materials',
        'parent_id': False,
    },
    {
        'name': 'Construction Labor',
        'parent_id': False,
    },
    {
        'name': 'Equipment Rental',
        'parent_id': False,
    },
    {
        'name': 'Project Overhead',
        'parent_id': False,
    },
    {
        'name': 'Permits & Legal Fees',
        'parent_id': False,
    },
]

# Create main categories
main_categories = {}
for cat_data in expense_categories:
    existing_cat = ProductCategory.search([('name', '=', cat_data['name']), ('parent_id', '=', False)])
    if not existing_cat:
        category = ProductCategory.create({
            'name': cat_data['name'],
        })
        main_categories[cat_data['name']] = category
        print(f"✅ Created expense category: {cat_data['name']}")
    else:
        main_categories[cat_data['name']] = existing_cat
        print(f"✅ Expense category already exists: {cat_data['name']}")

# Create subcategories for materials
materials_parent = main_categories.get('Construction Materials')
if materials_parent:
    subcategories = [
        'Concrete & Masonry', 'Steel & Metal', 'Lumber & Wood',
        'Electrical Materials', 'Plumbing Materials'
    ]
    for subcat_name in subcategories:
        existing_subcat = ProductCategory.search([('name', '=', subcat_name), ('parent_id', '=', materials_parent.id)])
        if not existing_subcat:
            ProductCategory.create({
                'name': subcat_name,
                'parent_id': materials_parent.id,
            })
            print(f"✅ Created subcategory: {subcat_name}")

# ====== STEP 4: UPDATE SAMPLE PROJECTS ======
print("\n🏗️  Step 4: Updating Sample Projects...")

# Get users for assignment
manager1 = Users.search([('login', '=', 'manager1')])
manager2 = Users.search([('login', '=', 'manager2')])
projectmgr1 = Users.search([('login', '=', 'projectmgr1')])

# Get the main partner for projects
main_partner = env.ref('base.main_partner', raise_if_not_found=False)
if not main_partner:
    main_partner = env['res.partner'].search([('is_company', '=', True)], limit=1)

# Project 1: Residential Building A
residential_project = Project.search([('name', '=', 'Residential Building A')])
if residential_project:
    # Update existing project with budget and details
    residential_project.write({
        'user_id': manager1.id if manager1 else False,
        'partner_id': main_partner.id if main_partner else False,
        'type_ids': [(6, 0, [stage.id for stage in created_stages])],
        'description': """
Residential Building Project - 3-story apartment complex

Budget: $150,000
Timeline: 8 months
Location: Downtown residential area

Scope:
- 12 apartment units
- Underground parking
- Modern amenities
- Energy-efficient design
        """,
    })
    print("✅ Updated existing project: Residential Building A")
else:
    residential_project = Project.create({
        'name': 'Residential Building A',
        'user_id': manager1.id if manager1 else False,
        'partner_id': main_partner.id if main_partner else False,
        'type_ids': [(6, 0, [stage.id for stage in created_stages])],
        'description': """
Residential Building Project - 3-story apartment complex

Budget: $150,000
Timeline: 8 months
Location: Downtown residential area

Scope:
- 12 apartment units
- Underground parking
- Modern amenities
- Energy-efficient design
        """,
    })
    print("✅ Created project: Residential Building A")

# Create analytic account for Residential Building A
residential_analytic = AnalyticAccount.search([('name', '=', 'Residential Building A')])
if not residential_analytic:
    residential_analytic = AnalyticAccount.create({
        'name': 'Residential Building A',
        'group_id': main_group.id,
        'partner_id': main_partner.id if main_partner else False,
    })
    residential_project.write({'analytic_account_id': residential_analytic.id})
    print("✅ Created analytic account for Residential Building A")

# Project 2: Commercial Office B
commercial_project = Project.search([('name', '=', 'Commercial Office B')])
if not commercial_project:
    commercial_project = Project.create({
        'name': 'Commercial Office B',
        'user_id': manager2.id if manager2 else False,
        'partner_id': main_partner.id if main_partner else False,
        'type_ids': [(6, 0, [stage.id for stage in created_stages])],
        'description': """
Commercial Office Building Project - 5-story office complex

Budget: $300,000
Timeline: 12 months
Location: Business district

Scope:
- 20,000 sq ft office space
- Modern HVAC system
- Advanced security systems
- LEED certification target
- Executive conference facilities
        """,
    })
    print("✅ Created project: Commercial Office B")
else:
    # Update existing project
    commercial_project.write({
        'user_id': manager2.id if manager2 else False,
        'partner_id': main_partner.id if main_partner else False,
        'type_ids': [(6, 0, [stage.id for stage in created_stages])],
        'description': """
Commercial Office Building Project - 5-story office complex

Budget: $300,000
Timeline: 12 months
Location: Business district

Scope:
- 20,000 sq ft office space
- Modern HVAC system
- Advanced security systems
- LEED certification target
- Executive conference facilities
        """,
    })
    print("✅ Updated existing project: Commercial Office B")

# Create analytic account for Commercial Office B
commercial_analytic = AnalyticAccount.search([('name', '=', 'Commercial Office B')])
if not commercial_analytic:
    commercial_analytic = AnalyticAccount.create({
        'name': 'Commercial Office B',
        'group_id': main_group.id,
        'partner_id': main_partner.id if main_partner else False,
    })
    commercial_project.write({'analytic_account_id': commercial_analytic.id})
    print("✅ Created analytic account for Commercial Office B")

# ====== STEP 5: CREATE SAMPLE TASKS FOR PROJECTS ======
print("\n📝 Step 5: Creating Sample Tasks...")

# Tasks for Residential Building A
residential_tasks = [
    {'name': 'Obtain Building Permits', 'stage': 'Planning & Design', 'priority': '1'},
    {'name': 'Site Survey and Analysis', 'stage': 'Planning & Design', 'priority': '1'},
    {'name': 'Clear and Level Site', 'stage': 'Site Preparation', 'priority': '0'},
    {'name': 'Excavate Foundation', 'stage': 'Foundation', 'priority': '0'},
    {'name': 'Pour Foundation Concrete', 'stage': 'Foundation', 'priority': '1'},
    {'name': 'Frame Structure', 'stage': 'Structure & Framing', 'priority': '0'},
    {'name': 'Install Electrical Rough-in', 'stage': 'MEP (Mechanical, Electrical, Plumbing)', 'priority': '0'},
    {'name': 'Install Plumbing Rough-in', 'stage': 'MEP (Mechanical, Electrical, Plumbing)', 'priority': '0'},
    {'name': 'Drywall and Paint', 'stage': 'Finishing', 'priority': '0'},
    {'name': 'Final Electrical and Plumbing', 'stage': 'Finishing', 'priority': '0'},
    {'name': 'Building Inspection', 'stage': 'Final Inspection', 'priority': '1'},
]

for task_data in residential_tasks:
    # Find stage by name
    stage = ProjectStage.search([('name', '=', task_data['stage'])], limit=1)
    if stage:
        existing_task = Task.search([
            ('name', '=', task_data['name']),
            ('project_id', '=', residential_project.id)
        ])
        if not existing_task:
            Task.create({
                'name': task_data['name'],
                'project_id': residential_project.id,
                'stage_id': stage.id,
                'priority': task_data['priority'],
                'user_ids': [(6, 0, [manager1.id])] if manager1 else [],
            })

print("✅ Created tasks for Residential Building A")

# Tasks for Commercial Office B
commercial_tasks = [
    {'name': 'Commercial Permits & Zoning', 'stage': 'Planning & Design', 'priority': '1'},
    {'name': 'Environmental Impact Assessment', 'stage': 'Planning & Design', 'priority': '1'},
    {'name': 'Site Preparation & Utilities', 'stage': 'Site Preparation', 'priority': '0'},
    {'name': 'Deep Foundation Work', 'stage': 'Foundation', 'priority': '1'},
    {'name': 'Steel Frame Erection', 'stage': 'Structure & Framing', 'priority': '1'},
    {'name': 'HVAC System Installation', 'stage': 'MEP (Mechanical, Electrical, Plumbing)', 'priority': '0'},
    {'name': 'Advanced Security Systems', 'stage': 'MEP (Mechanical, Electrical, Plumbing)', 'priority': '0'},
    {'name': 'Interior Finishing', 'stage': 'Finishing', 'priority': '0'},
    {'name': 'LEED Certification Review', 'stage': 'Final Inspection', 'priority': '1'},
    {'name': 'Final Code Compliance', 'stage': 'Final Inspection', 'priority': '1'},
]

for task_data in commercial_tasks:
    # Find stage by name
    stage = ProjectStage.search([('name', '=', task_data['stage'])], limit=1)
    if stage:
        existing_task = Task.search([
            ('name', '=', task_data['name']),
            ('project_id', '=', commercial_project.id)
        ])
        if not existing_task:
            Task.create({
                'name': task_data['name'],
                'project_id': commercial_project.id,
                'stage_id': stage.id,
                'priority': task_data['priority'],
                'user_ids': [(6, 0, [manager2.id])] if manager2 else [],
            })

print("✅ Created tasks for Commercial Office B")

# ====== STEP 6: VERIFICATION ======
print("\n🔍 Step 6: Verification Summary...")

all_projects = Project.search([('name', 'in', ['Residential Building A', 'Commercial Office B'])])
all_stages = ProjectStage.search([('name', 'in', [s['name'] for s in construction_stages])])
all_tasks = Task.search([('project_id', 'in', all_projects.ids)])

print(f"📊 Construction stages created: {len(all_stages)}")
print(f"📊 Sample projects: {len(all_projects)}")
print(f"📊 Project tasks created: {len(all_tasks)}")
print(f"📊 Expense categories created: {len(main_categories)}")

print("\n✅ Construction Project Structure Setup Complete!")

print("\n🏗️  Project Structure Created:")
print("├── Construction Stages (8 stages)")
print("├── Expense Categories (5+ categories)")
print("├── Sample Projects (2 projects)")
print("├── Project Tasks (20+ tasks)")
print("└── Analytic Accounts for tracking")

print("\n📋 Ready to Use:")
print("1. Go to Projects → Projects to see the structure")
print("2. Use Kanban view for visual project tracking")
print("3. Create expenses using the defined categories")
print("4. Track progress through construction stages")

print("\n🎯 Project Budgets:")
print("├── Residential Building A: $150,000")
print("└── Commercial Office B: $300,000")

print("\n✅ Setup completed successfully!")