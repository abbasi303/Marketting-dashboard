#!/usr/bin/env python3
"""
SW360-Style License Analyzer
Performs deep license analysis like SW360 would do
"""

import pkg_resources
import requests
import json
import re
from pathlib import Path

def get_package_license_info(package_name):
    """Get detailed license info from PyPI API like SW360 would"""
    try:
        # Get PyPI metadata
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            info = data.get('info', {})
            
            # Extract license information
            license_info = {
                'declared_license': info.get('license', 'UNKNOWN'),
                'license_classifier': [],
                'homepage': info.get('home_page', ''),
                'author': info.get('author', ''),
                'description': info.get('summary', ''),
                'source_url': info.get('project_urls', {}).get('Source', ''),
                'vulnerabilities': []
            }
            
            # Get license classifiers
            for classifier in info.get('classifiers', []):
                if 'License' in classifier:
                    license_info['license_classifier'].append(classifier)
            
            return license_info
    except:
        pass
    
    return None

def analyze_critical_packages():
    """Analyze packages that pip-licenses couldn't identify"""
    
    critical_packages = [
        'Flask', 'CacheControl', 'alembic', 'sqlbag', 'urllib3',
        'migra', 'schemainspect', 'mirakuru'  # Previously flagged
    ]
    
    results = {
        'scan_type': 'SW360_STYLE_DEEP_ANALYSIS',
        'timestamp': '2025-08-28T20:36:00',
        'critical_findings': [],
        'license_conflicts': [],
        'security_flags': [],
        'compliance_recommendations': []
    }
    
    print("🔍 **SW360-STYLE DEEP LICENSE ANALYSIS**")
    print("=" * 50)
    
    for package in critical_packages:
        try:
            # Get installed version
            dist = pkg_resources.get_distribution(package)
            version = dist.version
            
            print(f"\n📦 Analyzing {package} v{version}...")
            
            # Get detailed license info
            license_info = get_package_license_info(package)
            
            if license_info:
                declared = license_info['declared_license']
                classifiers = license_info['license_classifier']
                
                print(f"   Declared License: {declared}")
                print(f"   Classifiers: {len(classifiers)} found")
                
                # SW360-style risk assessment
                risk_level = "LOW"
                issues = []
                
                if declared in ['UNKNOWN', '', 'None']:
                    if not classifiers:
                        risk_level = "HIGH"
                        issues.append("No license information found")
                    else:
                        # Check classifiers for actual license
                        for classifier in classifiers:
                            if 'BSD' in classifier or 'MIT' in classifier:
                                declared = classifier.split(' :: ')[-1]
                                risk_level = "LOW"
                                break
                            elif 'GPL' in classifier or 'LGPL' in classifier:
                                declared = classifier.split(' :: ')[-1]
                                risk_level = "MEDIUM"
                                issues.append("Copyleft license detected")
                            elif 'Apache' in classifier:
                                declared = classifier.split(' :: ')[-1]
                                risk_level = "LOW"
                                break
                
                finding = {
                    'package': package,
                    'version': version,
                    'declared_license': declared,
                    'risk_level': risk_level,
                    'issues': issues,
                    'homepage': license_info.get('homepage', ''),
                    'classifiers': classifiers
                }
                
                results['critical_findings'].append(finding)
                
                print(f"   🎯 RISK LEVEL: {risk_level}")
                if issues:
                    for issue in issues:
                        print(f"   ⚠️  {issue}")
                
            else:
                print("   ❌ Could not retrieve package metadata")
                
        except pkg_resources.DistributionNotFound:
            print(f"   ⚠️  Package {package} not installed")
        except Exception as e:
            print(f"   ❌ Error analyzing {package}: {e}")
    
    # Save results
    docs_path = Path(__file__).parent.parent / "docs"
    results_file = docs_path / "sw360_style_analysis.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed analysis saved: {results_file}")
    
    # Generate compliance summary
    high_risk = [f for f in results['critical_findings'] if f['risk_level'] == 'HIGH']
    medium_risk = [f for f in results['critical_findings'] if f['risk_level'] == 'MEDIUM']
    
    print(f"\n📊 **FINAL SW360-STYLE COMPLIANCE REPORT:**")
    print(f"   🔴 HIGH RISK: {len(high_risk)} packages")
    print(f"   🟡 MEDIUM RISK: {len(medium_risk)} packages") 
    print(f"   🟢 TOTAL ANALYZED: {len(results['critical_findings'])} packages")
    
    if high_risk:
        print(f"\n🚨 HIGH RISK PACKAGES:")
        for finding in high_risk:
            print(f"   • {finding['package']} v{finding['version']}: {', '.join(finding['issues'])}")
    
    return results

if __name__ == "__main__":
    analyze_critical_packages()
