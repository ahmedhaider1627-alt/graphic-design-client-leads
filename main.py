#!/usr/bin/env python3
"""
Graphic Design Client Leads Generator
Main entry point for finding businesses needing design services
"""

import sys
import time
from pathlib import Path
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from config import Config
from models.database import init_db
from sources.twitter import TwitterScraper
from sources.reddit import RedditScraper
from sources.upwork import UpworkScraper
from sources.fiverr import FiverrScraper
from utils.logger import setup_logger

# Setup logging
setup_logger()

class LeadGeneratorEngine:
    """Main client lead generation engine"""
    
    def __init__(self):
        self.config = Config()
        self.scrapers = {}
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
        # Initialize database
        init_db()
        logger.info("Database initialized")
        
        # Initialize scrapers
        self._init_scrapers()
    
    def _init_scrapers(self):
        """Initialize all available scrapers"""
        logger.info("Initializing lead scrapers...")
        
        if 'twitter' in self.config.ENABLED_SOURCES:
            self.scrapers['twitter'] = TwitterScraper()
            logger.info("✓ Twitter scraper initialized")
        
        if 'reddit' in self.config.ENABLED_SOURCES:
            self.scrapers['reddit'] = RedditScraper()
            logger.info("✓ Reddit scraper initialized")
        
        if 'upwork' in self.config.ENABLED_SOURCES:
            self.scrapers['upwork'] = UpworkScraper()
            logger.info("✓ Upwork scraper initialized")
        
        if 'fiverr' in self.config.ENABLED_SOURCES:
            self.scrapers['fiverr'] = FiverrScraper()
            logger.info("✓ Fiverr scraper initialized")
    
    def run_once(self):
        """Run lead generation once"""
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
        logger.info(f"Next cycle in {self.config.CRAWL_INTERVAL} seconds")
        logger.info(f"{'='*60}\n")
    
    def start(self):
        """Start the lead generation engine"""
        if self.is_running:
            logger.warning("Engine is already running")
            return
        
        self.is_running = True
        logger.info("\n" + "="*60)
        logger.info("🚀 GRAPHIC DESIGN CLIENT LEADS GENERATOR STARTED")
        logger.info(f"Interval: {self.config.CRAWL_INTERVAL} seconds")
        logger.info(f"Min Budget: ${self.config.MIN_BUDGET}")
        logger.info(f"Min Quality Score: {self.config.MIN_QUALITY_SCORE}")
        logger.info(f"Max Results: {self.config.MAX_RESULTS}")
        logger.info("="*60 + "\n")
        
        # Run immediately
        self.run_once()
        
        # Schedule recurring runs
        self.scheduler.add_job(
            self.run_once,
            'interval',
            seconds=self.config.CRAWL_INTERVAL,
            id='lead_generation_cycle'
        )
        
        try:
            self.scheduler.start()
            logger.info("Scheduler started. Press Ctrl+C to stop.")
            
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
        logger.info("Engine stopped.")

def main():
    """Main entry point"""
    engine = LeadGeneratorEngine()
    
    try:
        engine.start()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
