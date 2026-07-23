import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    
    # Database
    DB_PATH = os.getenv('DB_PATH', './data/clients.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    LINKEDIN_COOKIES = os.getenv('LINKEDIN_COOKIES')
    HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')  # Email finder
    ROCKETREACH_API_KEY = os.getenv('ROCKETREACH_API_KEY')  # B2B data
    
    # Crawling Settings
    CRAWL_INTERVAL = int(os.getenv('CRAWL_INTERVAL', 1800))  # 30 minutes
    MIN_BUDGET = int(os.getenv('MIN_BUDGET', 500))
    MIN_QUALITY_SCORE = int(os.getenv('MIN_QUALITY_SCORE', 60))
    MAX_RESULTS = int(os.getenv('MAX_RESULTS', 5000))
    REQUEST_TIMEOUT = 30
    
    # Rate Limiting
    REQUESTS_PER_SECOND = 2
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    # Flask
    DEBUG = os.getenv('DEBUG', False)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    PORT = int(os.getenv('PORT', 5000))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')
    
    # Redis (optional caching)
    REDIS_URL = os.getenv('REDIS_URL')
    
    # Platforms to crawl
    ENABLED_SOURCES = [
        'twitter',
        'reddit',
        'fiverr',
        'upwork',
        'facebook',
        'linkedin',
        'google',
        'craigslist'
    ]
    
    # Keywords to search for design needs
    SEARCH_KEYWORDS = [
        'need designer',
        'looking for graphic design',
        'design project',
        'artwork needed',
        'hiring designer',
        'need logo',
        'need branding',
        'design help',
        'design freelancer',
        'graphic designer',
        'need website design',
        'social media graphics',
        'urgent design',
        'ASAP designer'
    ]
    
    # Project types to detect
    PROJECT_TYPES = [
        'Logo Design',
        'Branding',
        'Website Design',
        'Social Media Graphics',
        'Print Design',
        'Packaging Design',
        'Illustration',
        'Animation',
        'Video Editing',
        'UI/UX Design',
        'Business Cards',
        'Flyers & Posters',
        'Brand Identity',
        'Marketing Materials'
    ]
    
    # Budget detection keywords
    BUDGET_KEYWORDS = [
        'budget', 'price', 'cost', 'pay', 'rate', 'payment',
        'compensation', 'salary', 'hourly', 'fixed price'
    ]
    
    # Urgency indicators
    URGENCY_KEYWORDS = [
        'ASAP', 'urgent', 'deadline', 'immediate', 'quickly',
        'rush', 'time-sensitive', 'hurry', 'now', 'today'
    ]

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
