# SW360 Integration Guide - Marketing Insights Dashboard

## Overview
SW360 (Software 360°) is an enterprise license compliance and vulnerability management platform.

## Quick SW360 Setup

### Option 1: Cloud SW360 (Recommended)
1. **Register**: Go to https://sw360.eclipse.org/
2. **Create Project**: "Marketing Insights Dashboard"
3. **Upload Component List**: Use the generated SPDX file below

### Option 2: Local SW360 Instance
```bash
# Clone SW360 repository
git clone https://github.com/eclipse-sw360/sw360.git
cd sw360

# Start with Docker Compose  
docker-compose -f docker-compose.yml up -d

# Access SW360 at http://localhost:8080
# Default login: admin@sw360.org / sw360-password
```

## Component Export for SW360

### Generate SPDX Document:
```bash
# Install SPDX tools
pip install spdx-tools

# Generate SPDX file for SW360 import
python generate_spdx.py > docs/marketing-dashboard-spdx.json
```

### Manual SW360 Project Setup:
1. **Login to SW360**
2. **Create New Project**: 
   - Name: "Marketing Insights Dashboard"
   - Version: "1.0.0"
   - Project Type: "Product"
3. **Add Components**: Upload our component list
4. **Run Compliance Check**
5. **Export Clearing Report**

## Components for SW360 Import

### Core Dependencies (Production)
- Flask 3.1.1 (Web framework)
- pandas 2.3.2 (Data processing)  
- numpy 2.3.2 (Numerical computing)
- werkzeug 3.1.3 (WSGI toolkit)
- jinja2 3.1.6 (Template engine)

### Development Dependencies
- pytest 8.3.4 (Testing framework)
- pytest-cov 6.0.0 (Coverage reporting)
- pip-audit 2.9.0 (Security scanning)

### ⚠️ Flagged Components
- **migra** (Proprietary) - Database migration tool
- **schemainspect** (Proprietary) - Database inspection
- **mirakuru** (LGPL v3+) - Process management

## SW360 Workflow Commands

### 1. Export component list:
```bash
pip-licenses --format=csv --output-file=docs/sw360_components.csv
```

### 2. Generate vulnerability report:
```bash
pip-audit --format=json --output=docs/sw360_vulnerabilities.json
```

### 3. Create SW360 import file:
```bash
python scripts/generate_sw360_import.py
```

### 4. Upload to SW360 and run clearing:
- Import components via SW360 web interface
- Run automated license clearing
- Generate compliance report
- Export clearing decisions

## Expected SW360 Outputs

### Clearing Report Sections:
1. **License Obligations** - Required compliance actions
2. **Security Vulnerabilities** - CVE tracking and remediation  
3. **Export Control** - ECC classification if applicable
4. **Obligation Fulfillment** - License text requirements

### Deliverables:
- `docs/sw360_clearing_report.pdf`
- `docs/sw360_license_obligations.csv`  
- `docs/sw360_security_assessment.json`
- `docs/sw360_export_control.txt`

## Integration with CI/CD
```yaml
# Add to azure-pipelines.yml
- task: PythonScript@0
  displayName: 'Generate SW360 Export'
  inputs:
    scriptSource: 'filepath'
    scriptPath: 'scripts/sw360_export.py'
    
- task: PublishBuildArtifacts@1
  displayName: 'Publish SW360 Reports'
  inputs:
    pathToPublish: 'docs/sw360_*.json'
    artifactName: 'SW360-Reports'
```

## Manual Process (If no SW360 access)
1. **Export our component list**: `docs/compliance_summary.csv`
2. **Submit to legal team**: For manual license review
3. **Document findings**: In `docs/legal_review.md`
4. **Track remediation**: Update compliance status
