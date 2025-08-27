import os
from flask import Blueprint, render_template, jsonify, current_app, request
from app.services.analytics_service import generate_analytics_report

analytics_blueprint = Blueprint('analytics', __name__)

@analytics_blueprint.route('/analytics-report', methods=['GET'])
def get_analytics_report():
    """Generate and return the analytics report data"""
    report = generate_analytics_report()
    return jsonify(report)

@analytics_blueprint.route('/analytics')
def analytics_dashboard():
    """Render the analytics dashboard page"""
    return render_template('analytics_report.html')
