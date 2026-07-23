# Graphic Design Client Leads Generator

Automatically discover and generate leads for businesses and individuals who need graphic design services, artwork, or related design work.

## Features

- 🎯 **Business Lead Discovery** - Finds companies and individuals actively seeking design services
- 💼 **B2B & B2C Targeting** - Identifies both businesses and individual clients
- 📊 **Intent Detection** - Finds people posting about design needs on social media, forums, and job boards
- 🔍 **Opportunity Hunting** - Searches for design project opportunities and RFPs
- 💾 **Lead Database** - Stores prospects with contact info and project details
- 📧 **Email & Contact Extraction** - Automatically extracts business emails and contact information
- 🏆 **Lead Scoring** - Ranks leads by project budget, urgency, and quality
- 🔄 **Scheduled Crawling** - Continuously finds new opportunities
- 📈 **Web Dashboard** - View and manage prospects with notes and follow-up tracking
- 📦 **CSV Export** - Export leads for CRM or outreach campaigns

## How It Works

The system finds potential clients through:

1. **Social Media Monitoring** - Twitter, Facebook, Instagram posts about design needs
2. **Job Boards** - Fiverr/Upwork project postings looking for designers
3. **Business Directories** - Small businesses without websites or poor branding
4. **Forum Mining** - Reddit, Stack Overflow, industry forums asking for design help
5. **Local Business Listings** - Google Business, Yelp - new businesses needing branding
6. **Content Marketing** - Blog posts, Medium articles about design projects
7. **Twitter/X Search** - Real-time monitoring for "looking for designer" tweets
8. **Email Finding** - Extract business contact emails for outreach

## Installation

```bash
git clone https://github.com/ahmedhaider1627-alt/graphic-design-client-leads.git
cd graphic-design-client-leads
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file:

```env
# API Keys
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
GOOGLE_API_KEY=your_key
LINKEDIN_COOKIES=your_cookies

# Settings
CRAWL_INTERVAL=1800  # Run every 30 minutes
MIN_BUDGET=500  # Minimum project budget to track
MIN_QUALITY_SCORE=60

# Database
DB_PATH=./data/clients.db

# Keywords to search for
SEARCH_KEYWORDS=["need designer", "looking for graphic design", "design project", "artwork needed"]
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Run Lead Generator

```bash
python main.py
```

### Start Web Dashboard

```bash
python app.py
# Visit http://localhost:5000
```

### Run Specific Source

```bash
python -m sources.twitter      # Find Twitter posts needing designers
python -m sources.reddit       # Find Reddit requests for design help
python -m sources.upwork       # Find Upwork project postings
python -m sources.fiverr       # Find Fiverr gigs
python -m sources.facebook     # Find Facebook posts
python -m sources.linkedin     # Find LinkedIn opportunities
python -m sources.google       # Find local businesses
```

### Export Leads

```bash
python export.py --format csv --output prospects.csv
```

## Prospect Sources

### Online Platforms
- **Fiverr/Upwork** - Active project postings from clients seeking design work
- **Twitter/X** - Real-time "looking for designer" posts with high intent
- **Reddit** - r/forhire, r/slavelabour, design subreddits with project requests
- **Facebook Groups** - Business groups, entrepreneur communities asking for help
- **LinkedIn** - Companies hiring or posting about design projects
- **Craigslist** - Local design job postings

### Business Intelligence
- **Google Business Listings** - Newly created businesses without websites
- **Yelp** - Small businesses with poor branding/no professional images
- **Local Business Directories** - Restaurants, salons, services needing logos
- **Industry Directories** - Startup listings, new company databases

### Content & Forums
- **Stack Overflow** - Design-related questions
- **Designer Forums** - Project opportunities and collaborations
- **Medium/Dev.to** - Articles about design projects
- **GitHub Issues** - Design help requests in repositories

## Project Structure

```
.
├── main.py                    # Main entry point
├── app.py                     # Flask web app
├── requirements.txt           # Dependencies
├── config.py                  # Configuration
├── sources/                   # Lead scraping sources
│   ├── twitter.py            # Twitter/X monitoring
│   ├── reddit.py             # Reddit scraping
│   ├── fiverr.py             # Fiverr projects
│   ├── upwork.py             # Upwork projects
│   ├── facebook.py           # Facebook groups
│   ├── linkedin.py           # LinkedIn opportunities
│   ├── google.py             # Google Business
│   └── craigslist.py         # Craigslist listings
├── models/                    # Database models
│   └── database.py           # Lead/prospect models
├── utils/                     # Utility functions
│   ├── scraper.py            # Web scraping
│   ├── email_finder.py       # Email extraction
│   ├── scoring.py            # Lead scoring
│   └── logger.py             # Logging
├── scheduler.py              # Scheduled tasks
├── export.py                 # Export functionality
└── templates/                # Web UI
    ├── base.html
    ├── dashboard.html
    ├── prospects.html
    └── stats.html
```

## Lead Data Structure

```json
{
  "id": 1,
  "source": "twitter",
  "name": "John Smith",
  "business_name": "Smith Marketing Co",
  "project_type": "Logo Design",
  "project_description": "Need a modern logo for my marketing agency",
  "budget_estimate": 1500,
  "budget_range": "$1000-2000",
  "contact_email": "john@smithmarketing.com",
  "contact_phone": "+1234567890",
  "location": "New York, NY",
  "website": "https://smithmarketing.com",
  "social_profiles": ["@smithmarketing on Twitter"],
  "urgency": "high",
  "quality_score": 85,
  "raw_source_url": "https://twitter.com/...",
  "posted_date": "2024-01-15T10:30:00Z",
  "added_date": "2024-01-15T10:35:00Z",
  "contacted": false,
  "notes": "Active business, good budget, urgent need"
}
```

## API Endpoints

### Prospects
- `GET /api/prospects` - Get all prospects with filtering
- `GET /api/prospects/:id` - Get prospect details
- `GET /api/prospects/search?q=query` - Search prospects
- `POST /api/prospects/:id/contact` - Mark as contacted
- `DELETE /api/prospects/:id` - Remove prospect

### Statistics
- `GET /api/stats` - Dashboard statistics
- `GET /api/stats/by-source` - Leads by source
- `GET /api/stats/by-budget` - Distribution by budget
- `GET /api/stats/opportunities` - High-opportunity leads

### Export
- `GET /api/export?format=csv` - Export prospects
- `GET /api/export?format=json` - Export as JSON

## Dashboard Features

- 📊 Real-time prospect count and quality metrics
- 🎯 Filter by budget, urgency, source, and project type
- 📧 One-click email contact capture
- 📝 Notes and follow-up tracking
- ✅ Mark prospects as contacted/won
- 📈 Analytics on conversion rates
- 🔔 Alerts for high-value opportunities

## Scheduling

Default: crawls every 30 minutes for fresh opportunities

Adjust in `.env`:
```env
CRAWL_INTERVAL=1800  # 30 minutes
```

Or use cron for multiple sources:
```bash
# Check Twitter every 15 minutes
*/15 * * * * cd /path && python -m sources.twitter

# Check Upwork every 30 minutes
*/30 * * * * cd /path && python -m sources.upwork

# Full crawl every hour
0 * * * * cd /path && python main.py
```

## Database

SQLite stores all prospects:

```bash
sqlite3 data/clients.db
.tables
SELECT * FROM prospects WHERE contacted = 0 ORDER BY quality_score DESC;
```

## Smart Features

### Intent Detection
- Keywords: "need", "looking for", "hiring", "urgent", "ASAP"
- Budget mentions: "$500", "budget $1k", "up to $2000"
- Project types: "logo", "branding", "website design", "social media graphics"
- Urgency signals: "ASAP", "urgent", "deadline"

### Lead Scoring (0-100)
- Budget clarity (20 pts) - clear budget = higher score
- Urgency (20 pts) - urgent projects score higher
- Contact info (20 pts) - complete contact = better
- Business legitimacy (20 pts) - verified business higher
- Project clarity (20 pts) - detailed project description

### Duplicate Prevention
- Detects same person across multiple sources
- Merges duplicate leads
- Tracks which sources have the same prospect

## Rate Limiting

Respects platform limits:
- Twitter: 450 requests/15 min
- Reddit: 60 requests/minute
- Fiverr/Upwork: Custom delays
- Facebook: Respectful scraping only

## Legal Notice

- Comply with platform Terms of Service
- Respect robots.txt and rate limits
- Use appropriate User-Agent headers
- Do not spam or harass prospects
- Follow GDPR/CCPA email regulations
- Get consent before adding to mailing lists

## License

MIT License

## Support

For issues or questions, open an issue on GitHub.
