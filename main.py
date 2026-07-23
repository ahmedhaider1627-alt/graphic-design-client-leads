#!/usr/bin/env python3
"""
Graphic Design Client Leads Generator
Main entry point for finding businesses needing design services
"""

import sys
import os
import time
from pathlib import Path
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from app import app, db
from models.database import init_db
from utils.logger import setup_logger

# Setup logging
setup_logger()

class LeadGeneratorEngine:
    """Main client lead generation engine"""
    
    def __init__(self):
        self.scrapers = {}
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
        # Initialize database with app context
        with app.app_context():
            init_db()
            logger.info("Database initialized")
            self._init_scrapers()
    
    def _init_scrapers(self):
        """Initialize all available scrapers"""
        from config import Config
        
        config = Config()
        logger.info("Initializing lead scrapers...")
        
        if 'twitter' in config.ENABLED_SOURCES:
            try:
                from sources.twitter import TwitterScraper
                self.scrapers['twitter'] = TwitterScraper()
                logger.info("✓ Twitter scraper initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Twitter scraper: {str(e)}")
        
        if 'reddit' in config.ENABLED_SOURCES:
            try:
                from sources.reddit import RedditScraper
                self.scrapers['reddit'] = RedditScraper()
                logger.info("✓ Reddit scraper initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Reddit scraper: {str(e)}")
        
        if 'upwork' in config.ENABLED_SOURCES:
            try:
                from sources.upwork import UpworkScraper
                self.scrapers['upwork'] = UpworkScraper()
                logger.info("✓ Upwork scraper initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Upwork scraper: {str(e)}")
        
        if 'fiverr' in config.ENABLED_SOURCES:
            try:
                from sources.fiverr import FiverrScraper
                self.scrapers['fiverr'] = FiverrScraper()
                logger.info("✓ Fiverr scraper initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Fiverr scraper: {str(e)}")
    
    def run_once(self):
        """Run lead generation once"""
        with app.app_context():
            from config import Config
            config = Config()
            
            logger.info("=" * 60)
            logger.info(f"Starting lead generation cycle at {datetime.now()}")
            logger.info("=" * 60)
            
            total_prospects_found = 0
            
            for source_name, scraper in self.scrapers.items():
                try:
                    logger.info(f"\n🔍 Scraping {source_name.upper()}...")
                    prospects = scraper.scrape()
                    total_prospects_found += len(prospects)
                    logger.info(f"✓ Found {len(prospects)} prospects from {source_name}")
                except Exception as e:
                    logger.error(f"✗ Error scraping {source_name}: {str(e)}")
                    continue
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Cycle complete. Total prospects found: {total_prospects_found}")
            logger.info(f"Next cycle in {config.CRAWL_INTERVAL} seconds ({config.CRAWL_INTERVAL/60:.0f} minutes)")
            logger.info(f"{'='*60}\n")
    
    def start(self):
        """Start the lead generation engine"""
        if self.is_running:
            logger.warning("Engine is already running")
            return
        
        self.is_running = True
        
        with app.app_context():
            from config import Config
            config = Config()
            
            logger.info("\n" + "="*60)
            logger.info("🚀 GRAPHIC DESIGN CLIENT LEADS GENERATOR STARTED")
            logger.info(f"Interval: {config.CRAWL_INTERVAL} seconds ({config.CRAWL_INTERVAL/60:.0f} minutes)")
            logger.info(f"Min Budget: ${config.MIN_BUDGET}")
            logger.info(f"Min Quality Score: {config.MIN_QUALITY_SCORE}")
            logger.info(f"Max Results: {config.MAX_RESULTS}")
            logger.info("="*60 + "\n")
            
            # Run immediately
            self.run_once()
            
            # Schedule recurring runs
            self.scheduler.add_job(
                self.run_once,
                'interval',
                seconds=config.CRAWL_INTERVAL,
                id='lead_generation_cycle'
            )
        
        try:
            self.scheduler.start()
            logger.info("✓ Scheduler started. Press Ctrl+C to stop.")
            logger.info(f"📊 Dashboard: http://localhost:5000")
            
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the lead generation engine"""
        logger.info("\n" + "="*60)
        logger.info("⏹️  Stopping GRAPHIC DESIGN CLIENT LEADS GENERATOR")
        logger.info("="*60 + "\n")
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("✓ Engine stopped.")

def main():
    """Main entry point"""
    try:
        engine = LeadGeneratorEngine()
        engine.start()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
