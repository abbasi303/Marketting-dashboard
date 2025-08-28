#!/usr/bin/env python3
"""
SW360 Local Deployment Manager
Manages SW360 license compliance platform deployment and data import
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

class SW360Manager:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.docs_path = self.project_root / "docs"
        self.sw360_url = "http://localhost:8080"
        self.sw360_rest_url = "http://localhost:8091"
        self.admin_credentials = {"username": "admin@sw360.org", "password": "sw360admin"}
        
    def check_docker(self):
        """Check if Docker is available"""
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker available: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker not available. Please install Docker Desktop.")
            return False
    
    def deploy_sw360(self):
        """Deploy SW360 using docker-compose"""
        if not self.check_docker():
            return False
            
        compose_file = self.project_root / "docker-compose.sw360.yml"
        if not compose_file.exists():
            print(f"❌ Docker compose file not found: {compose_file}")
            return False
        
        print("🚀 Deploying SW360 platform...")
        print("This will take 5-10 minutes on first run (downloading images)")
        
        try:
            # Start SW360 services
            cmd = ["docker-compose", "-f", str(compose_file), "up", "-d"]
            subprocess.run(cmd, check=True, cwd=self.project_root)
            
            print("⏳ Waiting for SW360 services to initialize...")
            self.wait_for_services()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy SW360: {e}")
            return False
    
    def wait_for_services(self, timeout=600):  # 10 minutes timeout
        """Wait for SW360 services to be ready"""
        services = {
            "SW360 App": f"{self.sw360_url}/health",
            "SW360 REST API": f"{self.sw360_rest_url}/health"
        }
        
        start_time = time.time()
        ready_services = set()
        
        while len(ready_services) < len(services) and (time.time() - start_time) < timeout:
            for service_name, url in services.items():
                if service_name in ready_services:
                    continue
                    
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {service_name} is ready")
                        ready_services.add(service_name)
                except requests.exceptions.RequestException:
                    pass
            
            if len(ready_services) < len(services):
                print(f"⏳ Waiting for services... ({len(ready_services)}/{len(services)} ready)")
                time.sleep(10)
        
        if len(ready_services) == len(services):
            print("🎉 All SW360 services are ready!")
            return True
        else:
            print("⏰ Timeout waiting for services")
            return False
    
    def import_project_data(self):
        """Import our project data into SW360"""
        export_file = self.docs_path / "sw360_export.json"
        
        if not export_file.exists():
            print(f"❌ Export file not found: {export_file}")
            print("Run: python scripts/generate_sw360_export.py first")
            return False
        
        try:
            # Login to SW360
            login_data = {
                "username": self.admin_credentials["username"],
                "password": self.admin_credentials["password"]
            }
            
            session = requests.Session()
            login_response = session.post(f"{self.sw360_url}/api/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Failed to login to SW360: {login_response.status_code}")
                return False
            
            print("✅ Logged into SW360")
            
            # Import project data
            with open(export_file, 'r') as f:
                project_data = json.load(f)
            
            # Create project in SW360
            project_response = session.post(f"{self.sw360_rest_url}/api/projects", json=project_data)
            
            if project_response.status_code in [200, 201]:
                print("✅ Project imported successfully")
                project_id = project_response.json().get("id")
                print(f"📊 Project ID: {project_id}")
                return True
            else:
                print(f"❌ Failed to import project: {project_response.status_code}")
                print(f"Response: {project_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error importing data: {e}")
            return False
    
    def get_scan_results(self):
        """Get license compliance scan results"""
        try:
            session = requests.Session()
            login_data = {
                "username": self.admin_credentials["username"],
                "password": self.admin_credentials["password"]
            }
            session.post(f"{self.sw360_url}/api/login", json=login_data)
            
            # Get projects
            projects_response = session.get(f"{self.sw360_rest_url}/api/projects")
            
            if projects_response.status_code == 200:
                projects = projects_response.json()
                print(f"📋 Found {len(projects)} projects")
                
                for project in projects:
                    if "Marketing" in project.get("name", ""):
                        project_id = project["id"]
                        
                        # Get license compliance report
                        compliance_response = session.get(
                            f"{self.sw360_rest_url}/api/projects/{project_id}/licenses"
                        )
                        
                        if compliance_response.status_code == 200:
                            compliance_data = compliance_response.json()
                            
                            # Save compliance report
                            report_file = self.docs_path / "sw360_compliance_report.json"
                            with open(report_file, 'w') as f:
                                json.dump(compliance_data, f, indent=2)
                            
                            print(f"✅ Compliance report saved: {report_file}")
                            return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error getting scan results: {e}")
            return False
    
    def show_dashboard_urls(self):
        """Show SW360 dashboard URLs"""
        print("\n🌐 SW360 DASHBOARD ACCESS:")
        print(f"   Main Dashboard: {self.sw360_url}")
        print(f"   REST API: {self.sw360_rest_url}")
        print(f"   Username: {self.admin_credentials['username']}")
        print(f"   Password: {self.admin_credentials['password']}")
        print("\n📊 KEY FEATURES:")
        print("   • Component License Analysis")
        print("   • Vulnerability Scanning") 
        print("   • License Compliance Reports")
        print("   • Component Inventory Management")
        print("   • Export/Import Capabilities")
    
    def stop_sw360(self):
        """Stop SW360 services"""
        compose_file = self.project_root / "docker-compose.sw360.yml"
        try:
            cmd = ["docker-compose", "-f", str(compose_file), "down"]
            subprocess.run(cmd, check=True, cwd=self.project_root)
            print("✅ SW360 services stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stop SW360: {e}")

def main():
    manager = SW360Manager()
    
    if len(sys.argv) < 2:
        print("SW360 License Compliance Manager")
        print("\nUsage:")
        print("  python scripts/sw360_manager.py deploy    - Deploy SW360 platform")
        print("  python scripts/sw360_manager.py import    - Import project data")
        print("  python scripts/sw360_manager.py scan      - Get compliance results")
        print("  python scripts/sw360_manager.py dashboard - Show dashboard URLs")
        print("  python scripts/sw360_manager.py stop      - Stop SW360 services")
        return
    
    command = sys.argv[1].lower()
    
    if command == "deploy":
        if manager.deploy_sw360():
            manager.show_dashboard_urls()
    elif command == "import":
        manager.import_project_data()
    elif command == "scan":
        manager.get_scan_results()
    elif command == "dashboard":
        manager.show_dashboard_urls()
    elif command == "stop":
        manager.stop_sw360()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
