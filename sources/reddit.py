from sources.base_scraper import BaseScraper
from loguru import logger
from datetime import datetime
import time

class RedditScraper(BaseScraper):
    """Scrape Reddit for design service requests"""
    
    def __init__(self):
        super().__init__('reddit')
        # In production, use praw (Python Reddit API Wrapper)
    
    def scrape(self):
        """Scrape Reddit for design requests"""
        logger.info(f"Starting Reddit scrape at {datetime.now()}")
        start_time = time.time()
        
        try:
            prospects = []
            
            # Subreddits to search
            subreddits = [
                'forhire',
                'hireawriter',
                'slavelabour',
                'jobs',
                'freelance',
                'designjobs',
                'graphic_design'
            ]
            
            search_keywords = [
                'designer',
                'graphic design',
                'logo',
                'branding',
                'artwork',
                'illustration'
            ]
            
            for subreddit in subreddits:
                for keyword in search_keywords:
                    logger.info(f"Searching r/{subreddit}: {keyword}")
                    try:
                        subreddit_prospects = self._search_subreddit(subreddit, keyword)
                        prospects.extend(subreddit_prospects)
                        self.rate_limit()
                    except Exception as e:
                        logger.debug(f"Error searching r/{subreddit}: {str(e)}")
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
            
            logger.info(f"Reddit scrape complete. Found {len(prospects)} prospects.")
            return prospects
        
        except Exception as e:
            logger.error(f"Reddit scrape failed: {str(e)}")
            duration = time.time() - start_time
            self.log_crawl(
                status='failed',
                error=str(e),
                duration=duration
            )
            return []
    
    def _search_subreddit(self, subreddit_name, keyword):
        """Search for posts in a subreddit"""
        prospects = []
        
        # In production use praw:
        # reddit = praw.Reddit(...)
        # subreddit = reddit.subreddit(subreddit_name)
        # posts = subreddit.search(keyword)
        
        logger.info(f"Would search r/{subreddit_name} for: {keyword}")
        
        return prospects
    
    def _parse_post(self, post):
        """Parse Reddit post data"""
        text = post.get('title', '') + ' ' + post.get('selftext', '')
        
        # Extract budget
        min_budget, max_budget = self.extract_budget(text)
        budget_mentioned = min_budget is not None
        
        # Detect urgency
        urgency = self.detect_urgency(text)
        
        prospect = {
            'name': post.get('author', 'Anonymous'),
            'source': 'reddit',
            'project_description': text[:500],  # Limit to 500 chars
            'raw_source_url': f"https://reddit.com{post.get('permalink')}",
            'budget_estimate': min_budget,
            'budget_range': f"${min_budget}-{max_budget}" if min_budget else None,
            'budget_mentioned': budget_mentioned,
            'urgency': urgency,
            'social_profiles': [f"u/{post.get('author')}"],
            'posted_date': datetime.fromtimestamp(post.get('created_utc', 0))
        }
        
        prospect['quality_score'] = self.calculate_quality_score(prospect)
        
        return prospect
