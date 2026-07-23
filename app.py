#!/usr/bin/env python3
"""
Flask web application for viewing and managing design client leads
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models.database import db, Prospect, CrawlLog, ContactAttempt
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
from io import StringIO

app = Flask(__name__)

# Load config after app is created
from config import Config
config = Config()
app.config.from_object(config)

db.init_app(app)
CORS(app)

@app.before_request
def create_tables():
    """Create database tables if they don't exist"""
    with app.app_context():
        db.create_all()

# Web Routes

@app.route('/')
def index():
    """Dashboard home"""
    return render_template('dashboard.html')

@app.route('/prospects')
def prospects_page():
    """Prospects list page"""
    return render_template('prospects.html')

@app.route('/prospect/<int:prospect_id>')
def prospect_detail(prospect_id):
    """Prospect detail page"""
    prospect = Prospect.query.get_or_404(prospect_id)
    return render_template('prospect_detail.html', prospect=prospect)

@app.route('/stats')
def stats_page():
    """Statistics page"""
    return render_template('stats.html')

# API Routes

@app.route('/api/prospects')
def api_get_prospects():
    """Get all prospects with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort', 'quality_score', type=str)
    
    # Filtering
    query = Prospect.query
    
    # Source filter
    if request.args.get('source'):
        query = query.filter_by(source=request.args.get('source'))
    
    # Quality score filter
    min_score = request.args.get('min_score', type=int)
    if min_score:
        query = query.filter(Prospect.quality_score >= min_score)
    
    # Budget filter
    min_budget = request.args.get('min_budget', type=int)
    if min_budget:
        query = query.filter(Prospect.budget_estimate >= min_budget)
    
    # Urgency filter
    if request.args.get('urgency'):
        query = query.filter_by(urgency=request.args.get('urgency'))
    
    # Location filter
    if request.args.get('location'):
        query = query.filter(Prospect.location.ilike(f"%{request.args.get('location')}%"))
    
    # Contacted filter
    if request.args.get('contacted'):
        contacted = request.args.get('contacted').lower() == 'true'
        query = query.filter_by(contacted=contacted)
    
    # Sorting
    if sort_by == 'budget':
        query = query.order_by(Prospect.budget_estimate.desc().nullslast())
    elif sort_by == 'recent':
        query = query.order_by(Prospect.added_date.desc())
    elif sort_by == 'urgency':
        query = query.order_by(Prospect.urgency.desc())
    else:  # quality_score
        query = query.order_by(Prospect.quality_score.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'prospects': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@app.route('/api/prospects/<int:prospect_id>')
def api_get_prospect(prospect_id):
    """Get prospect details"""
    prospect = Prospect.query.get_or_404(prospect_id)
    return jsonify(prospect.to_dict())

@app.route('/api/prospects/search')
def api_search_prospects():
    """Search prospects"""
    query_str = request.args.get('q', '')
    
    if not query_str:
        return jsonify({'error': 'No query provided'}), 400
    
    prospects = Prospect.query.filter(
        (Prospect.name.ilike(f'%{query_str}%')) |
        (Prospect.business_name.ilike(f'%{query_str}%')) |
        (Prospect.project_description.ilike(f'%{query_str}%')) |
        (Prospect.email.ilike(f'%{query_str}%'))
    ).limit(50).all()
    
    return jsonify({
        'results': [p.to_dict() for p in prospects],
        'count': len(prospects)
    })

@app.route('/api/stats')
def api_get_stats():
    """Get dashboard statistics"""
    total_prospects = Prospect.query.count()
    contacted_prospects = Prospect.query.filter_by(contacted=True).count()
    won_prospects = Prospect.query.filter_by(status='won').count()
    
    # High value prospects (high score + high budget)
    high_value = Prospect.query.filter(
        Prospect.quality_score >= 80,
        Prospect.budget_estimate >= 1000
    ).count()
    
    # Prospects by source
    source_counts = db.session.query(
        Prospect.source,
        func.count(Prospect.id)
    ).group_by(Prospect.source).all()
    
    # Average budget by urgency
    urgency_budgets = db.session.query(
        Prospect.urgency,
        func.avg(Prospect.budget_estimate).label('avg_budget')
    ).filter(Prospect.budget_estimate.isnot(None)).group_by(Prospect.urgency).all()
    
    # Recent crawls
    recent_crawls = CrawlLog.query.order_by(
        CrawlLog.created_at.desc()
    ).limit(10).all()
    
    # Top sources by quality
    top_sources = db.session.query(
        Prospect.source,
        func.avg(Prospect.quality_score).label('avg_score')
    ).group_by(Prospect.source).order_by(func.avg(Prospect.quality_score).desc()).all()
    
    return jsonify({
        'total_prospects': total_prospects,
        'contacted_prospects': contacted_prospects,
        'conversion_rate': (contacted_prospects / total_prospects * 100) if total_prospects > 0 else 0,
        'won_prospects': won_prospects,
        'high_value_prospects': high_value,
        'source_distribution': [
            {'source': s[0], 'count': s[1]} for s in source_counts
        ],
        'avg_urgency_budgets': [
            {'urgency': u[0], 'budget': float(u[1]) if u[1] else 0} for u in urgency_budgets
        ],
        'top_sources': [
            {'source': s[0], 'score': float(s[1]) if s[1] else 0} for s in top_sources
        ],
        'recent_crawls': [
            {
                'source': c.source,
                'prospects_found': c.prospects_found,
                'status': c.status,
                'timestamp': c.created_at.isoformat()
            } for c in recent_crawls
        ]
    })

@app.route('/api/prospects/<int:prospect_id>/contact', methods=['POST'])
def api_mark_contacted(prospect_id):
    """Mark prospect as contacted"""
    prospect = Prospect.query.get_or_404(prospect_id)
    prospect.contacted = True
    prospect.contact_date = datetime.utcnow()
    
    # Log contact attempt
    data = request.get_json() or {}
    contact_log = ContactAttempt(
        prospect_id=prospect_id,
        contact_type=data.get('type', 'email'),
        contact_value=data.get('value'),
        status=data.get('status', 'sent'),
        message_sent=data.get('message')
    )
    
    prospect.status = data.get('status', 'contacted')
    
    db.session.add(contact_log)
    db.session.commit()
    
    return jsonify({'success': True, 'prospect': prospect.to_dict()})

@app.route('/api/prospects/<int:prospect_id>', methods=['DELETE'])
def api_delete_prospect(prospect_id):
    """Delete prospect"""
    prospect = Prospect.query.get_or_404(prospect_id)
    db.session.delete(prospect)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/export')
def api_export_prospects():
    """Export prospects as CSV"""
    prospects = Prospect.query.all()
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'id', 'name', 'business_name', 'email', 'phone',
        'location', 'website', 'source', 'project_type',
        'budget_estimate', 'urgency', 'quality_score',
        'status', 'raw_source_url', 'added_date'
    ])
    
    writer.writeheader()
    for prospect in prospects:
        row = prospect.to_dict()
        writer.writerow({k: row.get(k) for k in writer.fieldnames})
    
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=design_client_leads.csv'
    }

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=config.DEBUG, port=config.PORT, host='0.0.0.0')
