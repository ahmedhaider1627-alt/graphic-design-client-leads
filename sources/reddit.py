import praw
from sources.base_scraper import BaseScraper
from loguru import logger
from datetime import datetime
import time

class RedditScraper(BaseScraper):
    """Scrape Reddit for design service requests"""
    
    def __init__(self):
        super().__init__('reddit')
        self.reddit = None
        self._init_reddit()
    
    def _init_reddit(self):
        """Initialize Reddit API connection"""
        try:
            if not self.config.REDDIT_CLIENT_ID or not self.config.REDDIT_CLIENT_SECRET:
                logger.warning("⚠️  Reddit credentials not configured. Skipping Reddit scraper.")
                return
            
            self.reddit = praw.Reddit(
                client_id=self.config.REDDIT_CLIENT_ID,
                client_secret=self.config.REDDIT_CLIENT_SECRET,
                user_agent=self.config.REDDIT_USER_AGENT or 'graphic-design-leads/1.0'
            )
            
            # Test connection
            self.reddit.user.me()
            logger.info("✓ Reddit API connected successfully")
        
        except Exception as e:
            logger.error(f"❌ Reddit API connection failed: {str(e)}")
            logger.error("Make sure your credentials are correct in .env file")
            self.reddit = None
    
    def scrape(self):
        """Scrape Reddit for design requests"""
        if not self.reddit:
            logger.warning("Reddit API not initialized. Skipping.")
            return []
        
        logger.info(f"Starting Reddit scrape at {datetime.now()}")
        start_time = time.time()
        
        try:
            prospects = []
            
            # Subreddits to search
            subreddits = [
                'forhire',
                'slavelabour',
                'designjobs',
                'freelance',
                'jobs'
            ]
            
            search_keywords = [
                'designer',
                'graphic design',
                'logo',
                'branding',
                'artwork',
                'illustration',
                'design help'
            ]
            
            for subreddit_name in subreddits:
                for keyword in search_keywords:
                    logger.info(f"🔍 Searching r/{subreddit_name} for: {keyword}")
                    try:
                        subreddit_prospects = self._search_subreddit(subreddit_name, keyword)
                        prospects.extend(subreddit_prospects)
                        self.rate_limit()
                    except Exception as e:
                        logger.debug(f"Error searching r/{subreddit_name}: {str(e)}")
                        continue
            
            # Remove duplicates by URL
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
            
            logger.info(f"✓ Reddit scrape complete. Found {len(prospects)} prospects.")
            return prospects
        
        except Exception as e:
            logger.error(f"❌ Reddit scrape failed: {str(e)}")
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
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Search for posts with keyword (limit to last 50)
            for post in subreddit.search(keyword, sort='new', time_filter='week', limit=50):
                try:
                    # Skip if deleted or removed
                    if post.author is None or post.removed_by_category:
                        continue
                    
                    prospect = self._parse_post(post)
                    if prospect and prospect['quality_score'] >= self.config.MIN_QUALITY_SCORE:
                        prospects.append(prospect)
                
                except Exception as e:
                    logger.debug(f"Error parsing post: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error searching r/{subreddit_name}: {str(e)}")
        
        return prospects
    
    def _parse_post(self, post):
        """Parse Reddit post data"""
        try:
            # Combine title and body for full text
            text = post.title + ' ' + post.selftext
            
            # Extract budget
            min_budget, max_budget = self.extract_budget(text)
            budget_mentioned = min_budget is not None
            
            # Detect urgency
            urgency = self.detect_urgency(text)
            
            # Detect project type
            project_type = self._detect_project_type(text)
            
            prospect = {
                'name': post.author.name if post.author else 'Anonymous',
                'source': 'reddit',
                'project_type': project_type,
                'project_description': text[:500],  # Limit to 500 chars
                'raw_source_url': f"https://reddit.com{post.permalink}",
                'budget_estimate': min_budget,
                'budget_range': f"${min_budget}-{max_budget}" if min_budget else None,\n                'budget_mentioned': budget_mentioned,\n                'urgency': urgency,\n                'social_profiles': [f\"u/{post.author.name}\" if post.author else \"u/Anonymous\"],\n                'posted_date': datetime.fromtimestamp(post.created_utc)\n            }\n            \n            prospect['quality_score'] = self.calculate_quality_score(prospect)\n            \n            return prospect\n        \n        except Exception as e:\n            logger.debug(f\"Error parsing Reddit post: {str(e)}\")\n            return None\n    \n    def _detect_project_type(self, text):\n        \"\"\"Detect project type from text\"\"\"\n        text_lower = text.lower()\n        \n        project_types = {\n            'Logo Design': ['logo', 'icon'],\n            'Branding': ['brand', 'branding', 'identity'],\n            'Website Design': ['website', 'web design', 'web'],\n            'Illustration': ['illustration', 'illustrator', 'drawing'],\n            'Graphic Design': ['graphic design', 'graphics', 'design'],\n            'Social Media Graphics': ['social media', 'social graphics', 'instagram', 'facebook'],\n            'Artwork': ['artwork', 'art', 'painting', 'draw'],\n            'Animation': ['animation', 'animate', 'motion', 'video'],\n        }\n        \n        for ptype, keywords in project_types.items():\n            if any(kw in text_lower for kw in keywords):\n                return ptype\n        \n        return 'Graphic Design'  # Default\n