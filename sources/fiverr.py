from sources.base_scraper import BaseScraper
from loguru import logger
from datetime import datetime
import time

class FiverrScraper(BaseScraper):
    """Scrape Fiverr for design gig requests"""
    
    def __init__(self):
        super().__init__('fiverr')
        self.base_url = 'https://www.fiverr.com'
    
    def scrape(self):
        """Scrape Fiverr for design requests"""
        logger.info(f"Starting Fiverr scrape at {datetime.now()}")
        start_time = time.time()
        
        try:
            prospects = []
            
            # Search queries
            search_queries = [
                'graphic design',
                'logo design',
                'branding',
                'web design'
            ]
            
            for query in search_queries:
                logger.info(f"Searching Fiverr: {query}")
                try:
                    query_prospects = self._search_gigs(query)
                    prospects.extend(query_prospects)
                    self.rate_limit()
                except Exception as e:
                    logger.error(f"Error searching Fiverr: {str(e)}")
                    continue
            
            # Remove duplicates
            unique_prospects = {p['raw_source_url']: p for p in prospects}
            prospects = list(unique_prospects.values())
            
            # Save to database
            new_count, updated_count = self.save_prospects(prospects)
            
            duration = time.time() - start_time
            self.log_crawl(
                status='success',
                prospects_found=len(prospects),
                prospects_new=new_count,
                prospects_updated=updated_count,
                duration=duration
            )
            
            logger.info(f"Fiverr scrape complete. Found {len(prospects)} prospects.")
            return prospects
        
        except Exception as e:
            logger.error(f"Fiverr scrape failed: {str(e)}")
            duration = time.time() - start_time
            self.log_crawl(
                status='failed',
                error=str(e),
                duration=duration
            )
            return []
    
    def _search_gigs(self, query):
        """Search for gig requests"""
        prospects = []
        logger.info(f"Would search Fiverr for: {query}")
        return prospects
