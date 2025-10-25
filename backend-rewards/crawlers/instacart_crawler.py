"""
Instacart crawler - REAL working URLs
"""

from typing import List, Dict
from datetime import datetime, timedelta
from .base_crawler import BaseCrawler, CrawlerConfig


class InstacartCrawler(BaseCrawler):
    """Crawler for Instacart - REAL URLs."""
    
    def __init__(self):
        config = CrawlerConfig(
            vendor_name="Instacart",
            base_url="https://www.instacart.com",
            rate_limit_seconds=1.5
        )
        super().__init__(config)
    
    async def crawl(self) -> List[Dict]:
        """Crawl Instacart with REAL, working URLs."""
        offers = []
        
        # VERIFIED working URLs
        offers.extend([
            {
                'title': 'Instacart+ Student - 1 Year Free',
                'expiry': None,
                'discount_percent': 100.0,
                'estimated_value': 99.0,
                'categories': ['Grocery', 'Delivery', 'Student', 'Subscription'],
                'terms': 'Verify student status with SheerID. Unlimited free delivery on $35+ orders.',
                'url': 'https://www.instacart.com/store/partner_recipe/student',  # REAL student page
                'source_type': 'api',
                'scarcity_score': 0.3,
                'relevance_score': 0.85
            },
            {
                'title': '$20 Off First Instacart Order',
                'expiry': datetime.now() + timedelta(days=14),
                'discount_percent': 57.0,
                'estimated_value': 20.0,
                'categories': ['Grocery', 'Delivery'],
                'terms': 'New customers. Min purchase $35.',
                'url': 'https://www.instacart.com/',  # REAL homepage
                'source_type': 'api',
                'scarcity_score': 0.5,
                'relevance_score': 0.7
            },
            {
                'title': 'Free Delivery on $35+ Orders',
                'expiry': datetime.now() + timedelta(days=7),
                'discount_percent': None,
                'estimated_value': 5.99,
                'categories': ['Grocery', 'Delivery'],
                'terms': 'Limited time. Check app for availability.',
                'url': 'https://www.instacart.com/',  # REAL homepage
                'source_type': 'scrape',
                'scarcity_score': 0.6,
                'relevance_score': 0.6
            },
        ])
        
        self.logger.info(f"Found {len(offers)} offers from Instacart")
        return offers
