import requests
from abc import ABC, abstractmethod
from loguru import logger
from config import Config
from models.database import db, Prospect, CrawlLog
from datetime import datetime
import time
import re

class BaseScraper(ABC):
    """Base scraper class for all sources"""
    
    def __init__(self, source_name):
        self.source_name = source_name
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.USER_AGENT
        })
        self.prospects_found = []
    
    @abstractmethod
    def scrape(self):
        """Scrape prospects from the source"""
        pass
    
    def save_prospects(self, prospects):
        """Save prospects to database"""
        from app import app
        
        with app.app_context():
            new_count = 0
            updated_count = 0
            
            for prospect_data in prospects:
                try:
                    # Check if prospect already exists
                    existing = Prospect.query.filter_by(
                        raw_source_url=prospect_data['raw_source_url']
                    ).first()
                    
                    if existing:
                        # Update existing prospect
                        for key, value in prospect_data.items():
                            if hasattr(existing, key):
                                setattr(existing, key, value)
                        existing.updated_date = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Create new prospect
                        new_prospect = Prospect(**prospect_data)
                        db.session.add(new_prospect)
                        new_count += 1
                except Exception as e:
                    logger.error(f"Error saving prospect: {str(e)}")
                    continue
            
            try:
                db.session.commit()
                logger.info(f"✓ Saved {new_count} new prospects, updated {updated_count} prospects")
            except Exception as e:
                logger.error(f"Error committing to database: {str(e)}")
                db.session.rollback()
            
            return new_count, updated_count
    
    def log_crawl(self, status, prospects_found=0, prospects_new=0, prospects_updated=0, error=None, duration=0):
        """Log crawl activity"""
        from app import app
        
        with app.app_context():
            try:
                log = CrawlLog(
                    source=self.source_name,
                    prospects_found=prospects_found,
                    prospects_new=prospects_new,
                    prospects_updated=prospects_updated,
                    status=status,
                    error_message=error,
                    duration_seconds=duration
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                logger.error(f"Error logging crawl: {str(e)}")
    
    def get_request(self, url, **kwargs):
        """Make GET request with error handling"""
        try:
            response = self.session.get(
                url,
                timeout=self.config.REQUEST_TIMEOUT,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise
    
    def rate_limit(self):
        """Rate limiting to avoid overwhelming servers"""
        time.sleep(1 / self.config.REQUESTS_PER_SECOND)
    
    def extract_budget(self, text):
        """Extract budget information from text"""
        if not text:
            return None, None
        
        # Look for budget patterns like $500, $1k, $1,000
        patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $500, $1,000
            r'\$(\d+)k',  # $1k, $5k
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)',  # 500, 1,000
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            amounts.extend([int(m.replace(',', '')) for m in matches if m])
        
        if amounts:
            return min(amounts), max(amounts)
        return None, None
    
    def detect_urgency(self, text):
        """Detect urgency from text"""
        if not text:
            return 'low'
        
        text_lower = text.lower()
        urgency_keywords = self.config.URGENCY_KEYWORDS
        
        count = sum(1 for keyword in urgency_keywords if keyword.lower() in text_lower)
        
        if count >= 2:
            return 'high'
        elif count == 1:
            return 'medium'
        return 'low'
    
    def calculate_quality_score(self, prospect):
        """Calculate quality score for a prospect"""
        score = 50  # Base score
        
        # Contact info (25 points)
        if prospect.get('email'):
            score += 10
        if prospect.get('phone'):
            score += 8
        if prospect.get('location'):
            score += 7
        
        # Project clarity (25 points)
        if prospect.get('project_description'):
            desc_length = len(prospect.get('project_description', ''))
            if desc_length > 200:
                score += 15
            elif desc_length > 50:
                score += 10
            else:
                score += 5
        
        if prospect.get('project_type'):
            score += 10
        
        # Budget info (25 points)
        if prospect.get('budget_mentioned'):
            score += 15
        if prospect.get('budget_estimate'):
            score += 10
        
        # Urgency (25 points)
        urgency = prospect.get('urgency', 'low')
        if urgency == 'high':
            score += 25
        elif urgency == 'medium':
            score += 15
        else:
            score += 5
        
        return min(100, score)  # Cap at 100
