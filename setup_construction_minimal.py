#!/usr/bin/env python3
"""
Minimal Construction Project Setup Script for Odoo 17
Using only available models
"""

print("🏗️  Starting Construction Project Structure Setup...")

# Get required models
Project = env['project.project']
ProjectStage = env['project.project.stage']
Task = env['project.task']
AnalyticAccount = env['account.analytic.account']
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

# ====== STEP 2: CREATE EXPENSE PRODUCT CATEGORIES ======
print("\n🛠️  Step 2: Creating Expense Product Categories...")

expense_categories = [
    {'name': 'Construction Materials'},
    {'name': 'Construction Labor'},
    {'name': 'Equipment Rental'},
    {'name': 'Project Overhead'},
    {'name': 'Permits & Legal Fees'},
]

# Create main categories
main_categories = {}
for cat_data in expense_categories:
    existing_cat = ProductCategory.search([('name', '=', cat_data['name'])])
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

# ====== STEP 3: UPDATE SAMPLE PROJECTS ======
print("\n🏗️  Step 3: Updating Sample Projects...")

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
🏘️ Residential Building Project - 3-story apartment complex

💰 Budget: $150,000
⏱️ Timeline: 8 months
📍 Location: Downtown residential area

🎯 Scope:
- 12 apartment units
- Underground parking
- Modern amenities
- Energy-efficient design

📋 Construction Phases:
1. Planning & Design
2. Site Preparation
3. Foundation
4. Structure & Framing
5. MEP (Mechanical, Electrical, Plumbing)
6. Finishing
7. Final Inspection
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
🏘️ Residential Building Project - 3-story apartment complex

💰 Budget: $150,000
⏱️ Timeline: 8 months
📍 Location: Downtown residential area

🎯 Scope:
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
🏢 Commercial Office Building Project - 5-story office complex

💰 Budget: $300,000
⏱️ Timeline: 12 months
📍 Location: Business district

🎯 Scope:
- 20,000 sq ft office space
- Modern HVAC system
- Advanced security systems
- LEED certification target
- Executive conference facilities

📋 Construction Phases:
1. Planning & Design
2. Site Preparation
3. Foundation
4. Structure & Framing
5. MEP (Mechanical, Electrical, Plumbing)
6. Finishing
7. Final Inspection
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
🏢 Commercial Office Building Project - 5-story office complex

💰 Budget: $300,000
⏱️ Timeline: 12 months
📍 Location: Business district

🎯 Scope:
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
        'partner_id': main_partner.id if main_partner else False,
    })
    commercial_project.write({'analytic_account_id': commercial_analytic.id})
    print("✅ Created analytic account for Commercial Office B")

# ====== STEP 4: CREATE SAMPLE TASKS FOR PROJECTS ======
print("\n📝 Step 4: Creating Sample Tasks...")

# Tasks for Residential Building A
residential_tasks = [
    {'name': '📋 Obtain Building Permits', 'stage': 'Planning & Design', 'priority': '1'},
    {'name': '📐 Site Survey and Analysis', 'stage': 'Planning & Design', 'priority': '1'},
    {'name': '🚜 Clear and Level Site', 'stage': 'Site Preparation', 'priority': '0'},
    {'name': '⛏️ Excavate Foundation', 'stage': 'Foundation', 'priority': '0'},
    {'name': '🏗️ Pour Foundation Concrete', 'stage': 'Foundation', 'priority': '1'},
    {'name': '🔨 Frame Structure', 'stage': 'Structure & Framing', 'priority': '0'},
    {'name': '⚡ Install Electrical Rough-in', 'stage': 'MEP (Mechanical, Electrical, Plumbing)', 'priority': '0'},
    {'name': '🔧 Install Plumbing Rough-in', 'stage': 'MEP (Mechanical, Electrical, Plumbing)', 'priority': '0'},
    {'name': '🎨 Drywall and Paint', 'stage': 'Finishing', 'priority': '0'},
    {'name': '🔌 Final Electrical and Plumbing', 'stage': 'Finishing', 'priority': '0'},
    {'name': '✅ Building Inspection', 'stage': 'Final Inspection', 'priority': '1'},
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
    {'name': '📋 Commercial Permits & Zoning', 'stage': 'Planning & Design', 'priority': '1'},
    {'name': '🌍 Environmental Impact Assessment', 'stage': 'Planning & Design', 'priority': '1'},
    {'name': '🚧 Site Preparation & Utilities', 'stage': 'Site Preparation', 'priority': '0'},
    {'name': '🏗️ Deep Foundation Work', 'stage': 'Foundation', 'priority': '1'},
    {'name': '🏢 Steel Frame Erection', 'stage': 'Structure & Framing', 'priority': '1'},
    {'name': '❄️ HVAC System Installation', 'stage': 'MEP (Mechanical, Electrical, Plumbing)', 'priority': '0'},
    {'name': '🔒 Advanced Security Systems', 'stage': 'MEP (Mechanical, Electrical, Plumbing)', 'priority': '0'},
    {'name': '✨ Interior Finishing', 'stage': 'Finishing', 'priority': '0'},
    {'name': '🏆 LEED Certification Review', 'stage': 'Final Inspection', 'priority': '1'},
    {'name': '📝 Final Code Compliance', 'stage': 'Final Inspection', 'priority': '1'},
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

# ====== STEP 5: VERIFICATION ======
print("\n🔍 Step 5: Verification Summary...")

all_projects = Project.search([('name', 'in', ['Residential Building A', 'Commercial Office B'])])
all_stages = ProjectStage.search([('name', 'in', [s['name'] for s in construction_stages])])
all_tasks = Task.search([('project_id', 'in', all_projects.ids)])

print(f"📊 Construction stages created: {len(all_stages)}")
print(f"📊 Sample projects: {len(all_projects)}")
print(f"📊 Project tasks created: {len(all_tasks)}")
print(f"📊 Expense categories created: {len(main_categories)}")

print("\n✅ Construction Project Structure Setup Complete!")

print("\n🏗️  Project Structure Created:")
print("├── 📋 Construction Stages (8 stages)")
print("├── 🛠️  Expense Categories (5+ categories)")
print("├── 🏘️ Sample Projects (2 projects)")
print("├── 📝 Project Tasks (20+ tasks)")
print("└── 💰 Analytic Accounts for tracking")

print("\n📋 Construction Stages:")
for stage in created_stages:
    print(f"   {stage.sequence}. {stage.name}")

print("\n🏗️  Sample Projects:")
for project in all_projects:
    print(f"   ├── {project.name} (Manager: {project.user_id.name if project.user_id else 'None'})")

print("\n💰 Expense Categories:")
for name, category in main_categories.items():
    print(f"   ├── {name}")

print("\n📋 Ready to Use:")
print("1. Go to Projects → Projects to see the structure")
print("2. Use Kanban view for visual project tracking")
print("3. Create expenses using the defined categories")
print("4. Track progress through construction stages")

print("\n🎯 Project Budgets:")
print("├── 🏘️ Residential Building A: $150,000")
print("└── 🏢 Commercial Office B: $300,000")

print("\n✅ Setup completed successfully!")