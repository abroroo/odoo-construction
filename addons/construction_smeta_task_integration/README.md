# Construction Smeta Task Integration

This module extends the Russian smeta import functionality to create project tasks alongside budget lines, providing both financial tracking and project management capabilities.

## Features

### Dual Creation System
- **Budget Lines**: Maintains all existing financial tracking functionality
- **Project Tasks**: Adds full project management capabilities
- **Bidirectional Linking**: Tasks and budget lines are linked for integrated management

### Task Hierarchy
- **Main Tasks**: Created from smeta main items (1, 2, 3...)
- **Sub-Tasks**: Created from smeta sub-items (1.1, 1.2, 2.1...)
- **Parent-Child Relations**: Sub-tasks properly nested under main tasks

### Integration Features
- **Cross-References**: Budget lines link to tasks, tasks link to budget lines
- **Expense Tracking**: Direct expense creation from tasks
- **Progress Monitoring**: Task progress integrated with budget utilization
- **Over-Budget Alerts**: Visual indicators for budget overruns

## Workflow

### Import Process
1. Upload Russian smeta Excel file
2. System automatically creates:
   - Budget lines for financial tracking (existing functionality)
   - Project tasks for work management (new functionality)
   - Links between corresponding budget lines and tasks

### Project Management
1. **Task Assignment**: Assign tasks to team members
2. **Progress Tracking**: Track completion percentage
3. **Status Management**: Move tasks through stages (To Do → In Progress → Done)
4. **Dependencies**: Set task dependencies and scheduling

### Expense Management
1. **From Tasks**: Create expenses directly from task view
2. **From Budget Lines**: Record expenses against budget lines
3. **Automatic Linking**: Expenses automatically linked to both task and budget line

## Views & Navigation

### Project Module
- **Menu**: Project → Smeta Tasks
- **Views**: Kanban, Tree, Form, Calendar, Gantt
- **Features**: Task assignment, progress tracking, status management

### Construction Budget Module
- **Menu**: Construction Budget → Task Integration
- **Submenu**: Smeta Tasks, Budget Lines with Tasks
- **Features**: Budget vs actual tracking, expense management

### Enhanced Task Views
- **Budget Information**: Shows linked budget data in task form
- **Quick Actions**: View budget line, create expenses, view expenses
- **Status Indicators**: Over-budget alerts, budget utilization

### Enhanced Budget Views
- **Task Information**: Shows linked task data in budget line form
- **Quick Actions**: View task, create task, view task expenses
- **Progress Tracking**: Task progress integrated into budget views

## Technical Details

### Models Extended
- `construction.smeta.processor`: Enhanced to create tasks alongside budget lines
- `project.task`: Added smeta and budget integration fields
- `construction.project.budget.line`: Added task linking capabilities

### Key Fields Added
#### Project Task
- `smeta_number`: Original smeta task number
- `smeta_section`: РАЗДЕЛ section from smeta
- `smeta_type`: Main task or sub-task
- `budget_line_id`: Link to corresponding budget line
- Budget tracking fields (amount, spent, remaining, utilization)

#### Budget Line
- `task_id`: Link to corresponding project task
- Task tracking fields (stage, progress, assignee)

### Automatic Processing
- Russian smeta structure preserved in task hierarchy
- Task names from "НАИМЕНОВАНИЕ РАБОТ И РЕСУРСОВ" column
- Proper sequencing based on smeta numbering
- Automatic tagging of smeta-imported tasks

## Usage Examples

### For Project Managers
1. Import smeta file to create complete task structure
2. Assign tasks to team members
3. Track progress through Kanban boards
4. Monitor budget utilization per task
5. Identify over-budget tasks quickly

### For Site Managers
1. View assigned tasks in mobile-friendly Kanban view
2. Update task progress as work is completed
3. Create expenses directly from tasks
4. Track material usage against planned quantities

### For Accountants
1. Monitor budget vs actual spending per task
2. Identify budget overruns early
3. Track expense approvals linked to specific work items
4. Generate reports combining task progress and financial data

## Installation

1. Ensure dependencies are installed:
   - `construction_budget`
   - `construction_smeta_import`
   - `project`

2. Install this module:
   - Go to Apps → Search "Construction Smeta Task Integration"
   - Click Install

3. Import a Russian smeta file to see the dual creation in action

## Benefits

- **Unified Management**: Single import creates both financial and operational tracking
- **Better Visibility**: See both task progress and budget status together
- **Improved Control**: Early warning for budget overruns and delayed tasks
- **Enhanced Workflow**: Streamlined expense recording from task context
- **Complete Traceability**: Full audit trail from smeta → tasks → expenses