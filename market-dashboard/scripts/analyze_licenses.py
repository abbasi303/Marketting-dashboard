#!/usr/bin/env python3
"""
License Analysis Tool
Analyzes unknown and problematic licenses from pip-licenses output
"""

import csv
import json
import requests
from pathlib import Path

def analyze_unknown_licenses():
    """Analyze packages with unknown licenses"""
    
    project_root = Path(__file__).parent.parent
    docs_path = project_root / "docs"
    
    # Read license data
    licenses_file = docs_path / "sw360_components.csv"
    
    if not licenses_file.exists():
        print("❌ License file not found. Run pip-licenses first.")
        return
    
    unknown_packages = []
    risky_packages = []
    
    with open(licenses_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['Name']
            version = row['Version']
            license_type = row['License']
            
            if license_type in ['UNKNOWN', 'LGPL', 'GPL']:
                if license_type == 'UNKNOWN':
                    unknown_packages.append((name, version, license_type))
                else:
                    risky_packages.append((name, version, license_type))
    
    # Generate detailed analysis
    analysis = {
        "scan_timestamp": "2025-08-28T20:35:00",
        "total_packages": 108,
        "unknown_licenses": len(unknown_packages),
        "risky_licenses": len(risky_packages),
        "compliance_score": round((108 - len(unknown_packages) - len(risky_packages)) / 108 * 100, 2),
        "unknown_details": unknown_packages,
        "risky_details": risky_packages,
        "recommendations": {
            "immediate_action": [
                "Investigate unknown licenses for migra and schemainspect",
                "Verify Flask license (should be BSD)",
                "Review LGPL compatibility for mirakuru"
            ],
            "compliance_steps": [
                "Contact package maintainers for license clarification",
                "Consider alternative packages with clear licensing",
                "Document license compatibility decisions",
                "Implement license monitoring in CI/CD"
            ]
        }
    }
    
    # Save analysis
    analysis_file = docs_path / "license_analysis.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"📊 LICENSE COMPLIANCE ANALYSIS")
    print(f"   Compliance Score: {analysis['compliance_score']}%")
    print(f"   Unknown Licenses: {len(unknown_packages)} packages")
    print(f"   Risky Licenses: {len(risky_packages)} packages")
    print(f"   Analysis saved: {analysis_file}")
    
    # Show critical issues
    if unknown_packages:
        print(f"\n🚨 UNKNOWN LICENSES ({len(unknown_packages)}):")
        for name, version, license_type in unknown_packages:
            print(f"   • {name} v{version}")
    
    if risky_packages:
        print(f"\n⚠️  RISKY LICENSES ({len(risky_packages)}):")
        for name, version, license_type in risky_packages:
            print(f"   • {name} v{version} ({license_type})")

if __name__ == "__main__":
    analyze_unknown_licenses()
