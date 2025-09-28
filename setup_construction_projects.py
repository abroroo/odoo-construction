#!/usr/bin/env python3
"""
Construction Project Structure Setup Script for Odoo 17
Creates project templates, stages, categories, and sample projects
"""

def setup_construction_projects(env):
    """
    Complete setup for construction project management
    """
    print("🏗️  Starting Construction Project Structure Setup...")

    # Get required models
    Project = env['project.project']
    ProjectStage = env['project.project.stage']
    ProjectCategory = env['project.category']
    AnalyticAccount = env['account.analytic.account']
    AnalyticGroup = env['account.analytic.group']
    ExpenseCategory = env['product.category']
    ProductProduct = env['product.product']
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

    # ====== STEP 2: CREATE PROJECT CATEGORIES ======
    print("\n📂 Step 2: Creating Project Categories...")

    project_categories = [
        {'name': 'Residential Construction', 'color': 2},
        {'name': 'Commercial Construction', 'color': 5},
        {'name': 'Infrastructure Projects', 'color': 8},
        {'name': 'Renovation Projects', 'color': 10},
    ]

    created_categories = []
    for cat_data in project_categories:
        existing_cat = ProjectCategory.search([('name', '=', cat_data['name'])])
        if not existing_cat:
            category = ProjectCategory.create(cat_data)
            created_categories.append(category)
            print(f"✅ Created category: {cat_data['name']}")
        else:
            created_categories.append(existing_cat)
            print(f"✅ Category already exists: {cat_data['name']}")

    # ====== STEP 3: CREATE ANALYTIC GROUPS FOR EXPENSE TRACKING ======
    print("\n💰 Step 3: Creating Analytic Groups for Expense Tracking...")

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

    # ====== STEP 4: CREATE EXPENSE PRODUCT CATEGORIES ======
    print("\n🛠️  Step 4: Creating Expense Product Categories...")

    expense_categories = [
        {
            'name': 'Construction Materials',
            'parent_id': False,
            'property_cost_method': 'standard',
        },
        {
            'name': 'Concrete & Masonry',
            'parent_id': None,  # Will be set after creation
        },
        {
            'name': 'Steel & Metal',
            'parent_id': None,
        },
        {
            'name': 'Lumber & Wood',
            'parent_id': None,
        },
        {
            'name': 'Electrical Materials',
            'parent_id': None,
        },
        {
            'name': 'Plumbing Materials',
            'parent_id': None,
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

    # Create main categories first
    main_categories = {}
    for cat_data in expense_categories:
        if cat_data['parent_id'] is False:
            existing_cat = ExpenseCategory.search([('name', '=', cat_data['name']), ('parent_id', '=', False)])
            if not existing_cat:
                category = ExpenseCategory.create({
                    'name': cat_data['name'],
                    'property_cost_method': cat_data.get('property_cost_method', 'standard'),
                })
                main_categories[cat_data['name']] = category
                print(f"✅ Created expense category: {cat_data['name']}")
            else:
                main_categories[cat_data['name']] = existing_cat
                print(f"✅ Expense category already exists: {cat_data['name']}")

    # Create subcategories
    materials_parent = main_categories.get('Construction Materials')
    if materials_parent:
        subcategories = [
            'Concrete & Masonry', 'Steel & Metal', 'Lumber & Wood',
            'Electrical Materials', 'Plumbing Materials'
        ]
        for subcat_name in subcategories:
            existing_subcat = ExpenseCategory.search([('name', '=', subcat_name), ('parent_id', '=', materials_parent.id)])
            if not existing_subcat:
                ExpenseCategory.create({
                    'name': subcat_name,
                    'parent_id': materials_parent.id,
                })
                print(f"✅ Created subcategory: {subcat_name}")

    # ====== STEP 5: CREATE PROJECT TEMPLATES ======
    print("\n📋 Step 5: Creating Project Templates...")

    # Get users for assignment
    manager1 = Users.search([('login', '=', 'manager1')])
    manager2 = Users.search([('login', '=', 'manager2')])
    projectmgr1 = Users.search([('login', '=', 'projectmgr1')])

    # Template 1: Residential Construction
    residential_template = Project.search([('name', '=', 'TEMPLATE: Residential Construction')])
    if not residential_template:
        residential_template = Project.create({
            'name': 'TEMPLATE: Residential Construction',
            'is_template': True,
            'user_id': projectmgr1.id if projectmgr1 else False,
            'category_ids': [(6, 0, [cat.id for cat in created_categories if 'Residential' in cat.name])],
            'type_ids': [(6, 0, [stage.id for stage in created_stages])],
            'description': """
Standard template for residential construction projects.

Includes all construction phases from planning to completion.
Use this template for houses, apartments, and residential buildings.

Key Features:
- Pre-defined construction stages
- Budget tracking by category
- Resource planning
- Quality control checkpoints
            """,
        })
        print("✅ Created template: Residential Construction")

    # Template 2: Commercial Construction
    commercial_template = Project.search([('name', '=', 'TEMPLATE: Commercial Construction')])
    if not commercial_template:
        commercial_template = Project.create({
            'name': 'TEMPLATE: Commercial Construction',
            'is_template': True,
            'user_id': projectmgr1.id if projectmgr1 else False,
            'category_ids': [(6, 0, [cat.id for cat in created_categories if 'Commercial' in cat.name])],
            'type_ids': [(6, 0, [stage.id for stage in created_stages])],
            'description': """
Standard template for commercial construction projects.

Designed for office buildings, retail spaces, and commercial facilities.

Key Features:
- Extended MEP requirements
- Complex permitting processes
- Higher budget allocation
- Extended timeline planning
            """,
        })
        print("✅ Created template: Commercial Construction")

    # ====== STEP 6: CREATE SAMPLE PROJECTS ======
    print("\n🏗️  Step 6: Creating Sample Projects...")

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
            'category_ids': [(6, 0, [cat.id for cat in created_categories if 'Residential' in cat.name])],
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
            'category_ids': [(6, 0, [cat.id for cat in created_categories if 'Residential' in cat.name])],
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
            'plan_id': False,  # Default plan
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
            'category_ids': [(6, 0, [cat.id for cat in created_categories if 'Commercial' in cat.name])],
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
            'category_ids': [(6, 0, [cat.id for cat in created_categories if 'Commercial' in cat.name])],
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
            'plan_id': False,  # Default plan
        })
        commercial_project.write({'analytic_account_id': commercial_analytic.id})
        print("✅ Created analytic account for Commercial Office B")

    # ====== STEP 7: CREATE SAMPLE TASKS FOR PROJECTS ======
    print("\n📝 Step 7: Creating Sample Tasks...")

    Task = env['project.task']

    # Tasks for Residential Building A
    residential_tasks = [
        {'name': 'Obtain Building Permits', 'stage_id': created_stages[0].id, 'priority': '1'},
        {'name': 'Site Survey and Analysis', 'stage_id': created_stages[0].id, 'priority': '1'},
        {'name': 'Clear and Level Site', 'stage_id': created_stages[1].id, 'priority': '0'},
        {'name': 'Excavate Foundation', 'stage_id': created_stages[2].id, 'priority': '0'},
        {'name': 'Pour Foundation Concrete', 'stage_id': created_stages[2].id, 'priority': '1'},
        {'name': 'Frame Structure', 'stage_id': created_stages[3].id, 'priority': '0'},
        {'name': 'Install Electrical Rough-in', 'stage_id': created_stages[4].id, 'priority': '0'},
        {'name': 'Install Plumbing Rough-in', 'stage_id': created_stages[4].id, 'priority': '0'},
        {'name': 'Drywall and Paint', 'stage_id': created_stages[5].id, 'priority': '0'},
        {'name': 'Final Electrical and Plumbing', 'stage_id': created_stages[5].id, 'priority': '0'},
        {'name': 'Building Inspection', 'stage_id': created_stages[6].id, 'priority': '1'},
    ]

    for task_data in residential_tasks:
        existing_task = Task.search([
            ('name', '=', task_data['name']),
            ('project_id', '=', residential_project.id)
        ])
        if not existing_task:
            Task.create({
                'name': task_data['name'],
                'project_id': residential_project.id,
                'stage_id': task_data['stage_id'],
                'priority': task_data['priority'],
                'user_ids': [(6, 0, [manager1.id])] if manager1 else [],
            })

    print("✅ Created tasks for Residential Building A")

    # Tasks for Commercial Office B
    commercial_tasks = [
        {'name': 'Commercial Permits & Zoning', 'stage_id': created_stages[0].id, 'priority': '1'},
        {'name': 'Environmental Impact Assessment', 'stage_id': created_stages[0].id, 'priority': '1'},
        {'name': 'Site Preparation & Utilities', 'stage_id': created_stages[1].id, 'priority': '0'},
        {'name': 'Deep Foundation Work', 'stage_id': created_stages[2].id, 'priority': '1'},
        {'name': 'Steel Frame Erection', 'stage_id': created_stages[3].id, 'priority': '1'},
        {'name': 'HVAC System Installation', 'stage_id': created_stages[4].id, 'priority': '0'},
        {'name': 'Advanced Security Systems', 'stage_id': created_stages[4].id, 'priority': '0'},
        {'name': 'Interior Finishing', 'stage_id': created_stages[5].id, 'priority': '0'},
        {'name': 'LEED Certification Review', 'stage_id': created_stages[6].id, 'priority': '1'},
        {'name': 'Final Code Compliance', 'stage_id': created_stages[6].id, 'priority': '1'},
    ]

    for task_data in commercial_tasks:
        existing_task = Task.search([
            ('name', '=', task_data['name']),
            ('project_id', '=', commercial_project.id)
        ])
        if not existing_task:
            Task.create({
                'name': task_data['name'],
                'project_id': commercial_project.id,
                'stage_id': task_data['stage_id'],
                'priority': task_data['priority'],
                'user_ids': [(6, 0, [manager2.id])] if manager2 else [],
            })

    print("✅ Created tasks for Commercial Office B")

    # ====== STEP 8: VERIFICATION ======
    print("\n🔍 Step 8: Verification Summary...")

    all_projects = Project.search([('name', 'in', ['Residential Building A', 'Commercial Office B'])])
    all_templates = Project.search([('is_template', '=', True)])
    all_stages = ProjectStage.search([('name', 'in', [s['name'] for s in construction_stages])])

    print(f"📊 Construction stages created: {len(all_stages)}")
    print(f"📊 Project templates created: {len(all_templates)}")
    print(f"📊 Sample projects: {len(all_projects)}")
    print(f"📊 Expense categories created: {len(main_categories)}")

    print("\n✅ Construction Project Structure Setup Complete!")

    print("\n🏗️  Project Structure Created:")
    print("├── Construction Stages (8 stages)")
    print("├── Project Categories (4 categories)")
    print("├── Expense Categories (10+ categories)")
    print("├── Project Templates (2 templates)")
    print("├── Sample Projects (2 projects)")
    print("└── Analytic Accounts for tracking")

    print("\n📋 Next Steps:")
    print("1. Access Projects → Projects to see the structure")
    print("2. Use Kanban view for visual project tracking")
    print("3. Create expenses using the defined categories")
    print("4. Use templates to create new projects")

    return {
        'stages': created_stages,
        'categories': created_categories,
        'projects': all_projects,
        'templates': all_templates
    }

if __name__ == "__main__":
    print("This script should be run through Odoo shell")
    print("Usage: docker compose exec odoo odoo shell -d construction_business --no-http")