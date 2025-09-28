# Construction Smeta Import Module

A comprehensive Odoo 17 module for importing Excel smeta (budget estimate) files directly into construction project budgets.

## Features

### 🔧 Core Functionality
- **Excel File Import**: Support for .xls and .xlsx formats
- **Flexible Column Mapping**: Map any Excel columns to budget fields
- **Auto-Detection**: Intelligent column recognition for common headers
- **Russian Language Support**: Full support for Cyrillic text
- **Multi-Step Wizard**: User-friendly import process with preview
- **Error Handling**: Comprehensive error detection and reporting

### 📊 Data Processing
- **Budget Categories**: Auto-create or map to existing categories
- **Units of Measure**: Handle various UoM formats (m², kg, hours, etc.)
- **Calculations**: Auto-calculate totals when missing
- **Validation**: Data validation before import
- **Import Logging**: Complete audit trail of all imports

### 🏗️ Integration
- **Construction Budget Module**: Seamless integration with existing budgets
- **Project Management**: Link imports to specific projects
- **User Permissions**: Role-based access control
- **Multi-User Support**: Concurrent imports with user tracking

## Installation

### 1. Prerequisites

Ensure you have the required Python packages:

```bash
# Install inside your Odoo container
docker compose exec odoo pip install xlrd openpyxl
```

### 2. Module Dependencies

This module requires:
- `construction_budget` module (must be installed first)
- `project` (Odoo standard)
- `hr_expense` (Odoo standard)
- `purchase` (Odoo standard)

### 3. Install Module

```bash
# Install the module
docker compose exec odoo odoo -d your_database -i construction_smeta_import --stop-after-init --no-http

# Restart Odoo
docker compose restart odoo
```

### 4. Verify Installation

1. Login to Odoo
2. Go to **Construction Budget** menu
3. You should see:
   - **Import Smeta** (under Budget Management)
   - **Import Logs** (under Budget Management)
   - **Smeta Template** (under Configuration)

## Usage Guide

### Step 1: Prepare Excel File

Create an Excel file with the following columns (column names can vary):

| Column | Description | Example | Required |
|--------|-------------|---------|----------|
| Category | Budget category | Materials, Labor, Equipment | Optional |
| Item | Work/material description | Concrete foundation | **Required** |
| Quantity | Amount needed | 10.5 | Optional |
| Unit Price | Price per unit | 1500.00 | Optional |
| Total | Total amount | 15750.00 | Optional |
| Unit of Measure | Units | m², kg, hours | Optional |

**Sample Excel Content:**
```
Category        | Item                    | Quantity | Unit Price | Total    | Unit
Materials       | Concrete C25/30         | 10.5     | 2500.00    | 26250.00 | m³
Materials       | Steel reinforcement     | 2500     | 1.85       | 4625.00  | kg
Labor           | Concrete pouring        | 8        | 850.00     | 6800.00  | hours
Equipment       | Concrete mixer rental   | 3        | 1200.00    | 3600.00  | days
```

### Step 2: Import Process

1. **Navigate to Import**:
   - Go to **Construction Budget** → **Budget Management** → **Import Smeta**

2. **Upload File**:
   - Select your project
   - Choose existing budget or leave empty to create new one
   - Upload your Excel file
   - Click **Next**

3. **Map Columns**:
   - Review auto-detected column mappings
   - Adjust mappings if needed
   - Set header row and data start row
   - Click **Preview**

4. **Preview Data**:
   - Review first 10 rows of import data
   - Verify everything looks correct
   - Click **Import Now**

5. **Review Results**:
   - Check import summary
   - View any errors or warnings
   - Click **View Budget** to see results

### Step 3: Verify Import

1. **Check Budget**:
   - Go to **Construction Budget** → **Budget Management** → **Project Budgets**
   - Open your project's budget
   - Verify budget lines were created correctly

2. **Review Import Log**:
   - Go to **Construction Budget** → **Budget Management** → **Import Logs**
   - Check import statistics and any error messages

## Excel Template

### Download Template

Use the built-in template generator:
1. Go to **Import Smeta** wizard
2. Click **Download Template**
3. Follow the template structure

### Template File

A sample CSV template is available at:
```
/addons/construction_smeta_import/static/files/smeta_template.csv
```

You can open this in Excel and save as .xlsx format.

## Advanced Features

### Column Auto-Mapping

The module automatically detects columns based on common names:

**Category**: category, категория, раздел, тип, group, группа
**Item**: item, description, наименование, описание, работы, материал, name
**Quantity**: quantity, qty, количество, кол-во, кол, объем
**Unit Price**: unit_price, price, цена, стоимость, расценка, unit cost
**Total**: total, amount, сумма, итого, всего, стоимость общая
**UoM**: unit, uom, measure, единица, ед.изм, ед, изм

### Error Handling

Common errors and solutions:

| Error | Solution |
|-------|----------|
| "Item name is required" | Ensure item column has values |
| "Unsupported file format" | Use .xls or .xlsx files only |
| "No file to import" | Upload an Excel file first |
| "Error reading Excel file" | Check file is not corrupted |

### Russian Text Support

The module fully supports Russian text in:
- Column headers (категория, наименование, количество, etc.)
- Item descriptions and categories
- Units of measure (м², кг, час, etc.)
- All text fields

### Performance

- **Large Files**: Handles files with thousands of rows
- **Memory Efficient**: Processes files in chunks
- **Error Recovery**: Continues processing after non-fatal errors
- **Audit Trail**: Complete logging of all operations

## Troubleshooting

### Python Dependencies

If you get import errors, install required packages:

```bash
docker compose exec odoo pip install xlrd openpyxl
```

### Permission Errors

Ensure users have proper access rights:
- Base User access for import functionality
- Project Manager access for all projects
- System Administrator for module configuration

### File Format Issues

- Save Excel files in .xlsx or .xls format
- Avoid merged cells in data area
- Keep headers in first row
- Remove empty columns between data

### Memory Issues

For very large files:
- Split into smaller files (recommended: < 5000 rows)
- Import during off-peak hours
- Monitor server memory usage

## Technical Details

### Module Structure
```
construction_smeta_import/
├── __manifest__.py
├── models/
│   └── smeta_import.py
├── wizard/
│   ├── smeta_import_wizard.py
│   └── smeta_import_wizard_views.xml
├── views/
│   ├── smeta_import_views.xml
│   └── smeta_import_menu.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── smeta_template.xml
└── static/
    ├── description/
    └── files/
        └── smeta_template.csv
```

### Key Models

- `construction.smeta.import.log`: Import history and logs
- `construction.smeta.processor`: Excel processing engine
- `construction.smeta.import.wizard`: Import wizard interface
- `construction.smeta.import.preview`: Data preview functionality

### Dependencies

- **xlrd**: For .xls file reading
- **openpyxl**: For .xlsx file reading
- **construction_budget**: Core budget functionality
- **project**: Project management

## Support

### Common Issues

1. **Module won't install**: Check dependencies are installed first
2. **Excel files won't read**: Verify Python packages are installed
3. **Import fails**: Check file format and required columns
4. **Permission denied**: Verify user access rights

### Logs and Debugging

Check import logs in:
- **Odoo Interface**: Construction Budget → Import Logs
- **Server Logs**: Docker container logs
- **Database**: `construction_smeta_import_log` table

### Version Compatibility

- **Odoo Version**: 17.0+
- **Python**: 3.8+
- **Excel Formats**: .xls, .xlsx, .xlsm

---

## License

LGPL-3 License - Same as Odoo Community Edition

## Author

Construction Management System - Custom Odoo Development