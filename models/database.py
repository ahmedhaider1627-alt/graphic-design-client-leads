from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

db = SQLAlchemy()

class Prospect(db.Model):
    """Prospect/Lead model for client database storage"""
    __tablename__ = 'prospects'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal info
    name = db.Column(db.String(255), nullable=False, index=True)
    business_name = db.Column(db.String(255), index=True)
    
    # Contact info
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(255), index=True)
    website = db.Column(db.String(1000))
    social_profiles = db.Column(db.JSON)  # List of social media links
    
    # Project info
    source = db.Column(db.String(50), nullable=False, index=True)  # twitter, reddit, upwork, etc.
    project_type = db.Column(db.String(255))  # Logo Design, Branding, etc.
    project_description = db.Column(db.Text)  # Full project description
    raw_source_url = db.Column(db.String(1000), unique=True, nullable=False)  # Original post URL
    
    # Budget info
    budget_estimate = db.Column(db.Integer)  # Estimated budget in USD
    budget_range = db.Column(db.String(100))  # "$500-1000", "$1k+", etc.
    budget_mentioned = db.Column(db.Boolean, default=False)  # Was budget explicitly mentioned?
    
    # Urgency & Quality
    urgency = db.Column(db.String(50))  # low, medium, high
    quality_score = db.Column(db.Integer, default=0, index=True)  # 0-100
    
    # Timestamps
    posted_date = db.Column(db.DateTime, index=True)  # When project was posted
    added_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_checked = db.Column(db.DateTime)
    
    # Contact & Status
    contacted = db.Column(db.Boolean, default=False, index=True)
    contact_date = db.Column(db.DateTime)
    contact_method = db.Column(db.String(50))  # email, dm, comment, etc.
    status = db.Column(db.String(50), default='new')  # new, contacted, responded, won, lost
    notes = db.Column(db.Text)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'business_name': self.business_name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'website': self.website,
            'social_profiles': self.social_profiles,
            'source': self.source,
            'project_type': self.project_type,
            'project_description': self.project_description,
            'raw_source_url': self.raw_source_url,
            'budget_estimate': self.budget_estimate,
            'budget_range': self.budget_range,
            'budget_mentioned': self.budget_mentioned,
            'urgency': self.urgency,
            'quality_score': self.quality_score,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'added_date': self.added_date.isoformat(),
            'contacted': self.contacted,
            'contact_date': self.contact_date.isoformat() if self.contact_date else None,
            'contact_method': self.contact_method,
            'status': self.status,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Prospect {self.name} - {self.source}>'

class ContactAttempt(db.Model):
    """Track outreach attempts"""
    __tablename__ = 'contact_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    prospect_id = db.Column(db.Integer, db.ForeignKey('prospects.id'), nullable=False)
    contact_type = db.Column(db.String(50))  # email, dm, comment, phone
    contact_value = db.Column(db.String(500))  # email address, DM link, etc.
    status = db.Column(db.String(50))  # sent, pending, bounced, responded
    response = db.Column(db.Text)  # Response message if any
    message_sent = db.Column(db.Text)  # What message was sent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    prospect = db.relationship('Prospect', backref='contact_attempts')

class CrawlLog(db.Model):
    """Track scraping activities"""
    __tablename__ = 'crawl_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False, index=True)
    prospects_found = db.Column(db.Integer, default=0)
    prospects_new = db.Column(db.Integer, default=0)
    prospects_updated = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50))  # success, failed, partial
    error_message = db.Column(db.Text)
    duration_seconds = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

def init_db():
    """Initialize database tables"""
    db.create_all()
