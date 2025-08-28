#!/usr/bin/env python3
"""
SW360 Component Export Generator
Creates SW360-compatible import files for Marketing Insights Dashboard
"""

import json
import csv
import pandas as pd
from datetime import datetime

def generate_sw360_export():
    """Generate SW360-compatible component export"""
    
    # Read our license data
    with open('docs/licenses.json', 'r') as f:
        licenses_data = json.load(f)
    
    # Read vulnerability data  
    with open('docs/audit.json', 'r') as f:
        audit_data = json.load(f)
    
    # Create SW360 project structure
    sw360_project = {
        "name": "Marketing Insights Dashboard",
        "version": "1.0.0",
        "description": "Flask-based marketing analytics dashboard with KPI calculations and visualizations",
        "projectType": "PRODUCT",
        "businessUnit": "Analytics",
        "tag": "marketing-dashboard",
        "projectResponsible": "Development Team",
        "created": datetime.now().isoformat(),
        "components": []
    }
    
    # Process each component
    for package in licenses_data:
        component = {
            "name": package["Name"],
            "version": package["Version"], 
            "license": package["License"],
            "componentType": "OSS",
            "categories": ["Framework", "Library"],
            "homepage": f"https://pypi.org/project/{package['Name']}/",
            "downloadUrl": f"https://pypi.org/project/{package['Name']}/{package['Version']}/",
            "riskAssessment": get_risk_level(package["License"]),
            "clearingState": get_clearing_state(package["License"]),
            "vulnerabilities": get_vulnerabilities(package["Name"], audit_data)
        }
        sw360_project["components"].append(component)
    
    # Write SW360 export
    with open('docs/sw360_export.json', 'w') as f:
        json.dump(sw360_project, f, indent=2)
    
    print(f"✅ SW360 export generated: docs/sw360_export.json")
    print(f"📊 Components: {len(sw360_project['components'])}")
    print(f"⚠️  High-risk components: {len([c for c in sw360_project['components'] if c['riskAssessment'] == 'HIGH'])}")

def get_risk_level(license_name):
    """Determine risk level based on license"""
    if not license_name or license_name == "UNKNOWN":
        return "MEDIUM"
    elif "Proprietary" in license_name or "Other/" in license_name:
        return "HIGH"  
    elif "GPL" in license_name and "LGPL" not in license_name:
        return "HIGH"
    elif "LGPL" in license_name:
        return "MEDIUM"
    else:
        return "LOW"

def get_clearing_state(license_name):
    """Determine clearing state"""
    risk = get_risk_level(license_name)
    if risk == "HIGH":
        return "NEW_CLEARING"
    elif risk == "MEDIUM": 
        return "UNDER_CLEARING"
    else:
        return "APPROVED"

def get_vulnerabilities(package_name, audit_data):
    """Get vulnerabilities for package"""
    vulns = []
    for dep in audit_data.get("dependencies", []):
        if dep["name"].lower() == package_name.lower():
            vulns = dep.get("vulns", [])
            break
    return len(vulns)

if __name__ == "__main__":
    generate_sw360_export()
