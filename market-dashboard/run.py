#!/usr/bin/env python3
"""
Development server runner for Marketing Insights Dashboard
"""

import os
from app import app

if __name__ == '__main__':
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("🚀 Starting Marketing Insights Dashboard...")
    print("📊 Dashboard URL: http://localhost:5000")
    print("🔧 Health Check: http://localhost:5000/healthz")
    print("📋 API Docs: See README.md for API endpoints")
    print("👤 Role Management: http://localhost:5000/set-role")
    print()
    
    # Run the Flask development server
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
