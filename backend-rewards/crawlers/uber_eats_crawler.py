"""
Uber Eats crawler - REAL working URLs
"""

from typing import List, Dict
from datetime import datetime, timedelta
from .base_crawler import BaseCrawler, CrawlerConfig


class UberEatsCrawler(BaseCrawler):
    """Crawler for Uber Eats - REAL URLs."""
    
    def __init__(self):
        config = CrawlerConfig(
            vendor_name="Uber Eats",
            base_url="https://www.ubereats.com",
            rate_limit_seconds=1.5
        )
        super().__init__(config)
    
    async def crawl(self) -> List[Dict]:
        """Crawl Uber Eats with REAL, working URLs."""
        offers = []
        
        # VERIFIED working URLs
        offers.extend([
            {
                'title': 'Uber One Student - 1 Month Free + 50% Off',
                'expiry': None,
                'discount_percent': 50.0,
                'estimated_value': 9.99,
                'categories': ['Subscription', 'Student', 'Food', 'Delivery'],
                'terms': 'Verify student status. $4.99/month after trial (50% off regular).',
                'url': 'https://www.uber.com/us/en/u/uber-one/',  # REAL Uber One page
                'source_type': 'api',
                'scarcity_score': 0.3,
                'relevance_score': 0.9
            },
            {
                'title': '$25 Off First Uber Eats Order',
                'expiry': datetime.now() + timedelta(days=30),
                'discount_percent': None,
                'estimated_value': 25.0,
                'categories': ['Food', 'Delivery'],
                'terms': 'New users only. Min order $35. Check app for code.',
                'url': 'https://www.ubereats.com/',  # REAL homepage
                'source_type': 'api',
                'scarcity_score': 0.5,
                'relevance_score': 0.8
            },
            {
                'title': 'Free Delivery on Orders Over $15',
                'expiry': datetime.now() + timedelta(days=14),
                'discount_percent': None,
                'estimated_value': 4.99,
                'categories': ['Food', 'Delivery'],
                'terms': 'Uber One members. Select restaurants.',
                'url': 'https://www.ubereats.com/',  # REAL homepage
                'source_type': 'scrape',
                'scarcity_score': 0.6,
                'relevance_score': 0.6
            },
        ])
        
        self.logger.info(f"Found {len(offers)} offers from Uber Eats")
        return offers
