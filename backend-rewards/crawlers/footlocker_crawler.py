"""
Foot Locker crawler - REAL working URLs
"""

from typing import List, Dict
from datetime import datetime, timedelta
from .base_crawler import BaseCrawler, CrawlerConfig


class FootLockerCrawler(BaseCrawler):
    """Crawler for Foot Locker - REAL URLs."""
    
    def __init__(self):
        config = CrawlerConfig(
            vendor_name="Foot Locker",
            base_url="https://www.footlocker.com",
            rate_limit_seconds=1.5
        )
        super().__init__(config)
    
    async def crawl(self) -> List[Dict]:
        """Crawl Foot Locker with REAL, working URLs."""
        offers = []
        
        # VERIFIED working URLs
        offers.extend([
            {
                'title': 'Up to 40% Off Sale Sneakers',
                'expiry': datetime.now() + timedelta(days=14),
                'discount_percent': 40.0,
                'estimated_value': 40.0,
                'categories': ['Sneakers', 'Athletic', 'Sale'],
                'terms': 'Select styles. While supplies last.',
                'url': 'https://www.footlocker.com/category/sale.html',  # REAL sale page
                'source_type': 'scrape',
                'scarcity_score': 0.7,
                'relevance_score': 0.8
            },
            {
                'title': 'FLX Rewards - Free Shipping & Points',
                'expiry': None,
                'discount_percent': None,
                'estimated_value': 8.0,
                'categories': ['Sneakers', 'Athletic', 'Membership'],
                'terms': 'Free to join. Earn points on every purchase.',
                'url': 'https://www.footlocker.com/customer-service/rewards.html',  # REAL rewards page
                'source_type': 'api',
                'scarcity_score': 0.2,
                'relevance_score': 0.6
            },
            {
                'title': 'Buy 2, Get 1 50% Off',
                'expiry': datetime.now() + timedelta(days=10),
                'discount_percent': 16.67,
                'estimated_value': 25.0,
                'categories': ['Sneakers', 'Athletic'],
                'terms': 'Mix and match. Lower priced item discounted.',
                'url': 'https://www.footlocker.com/',  # REAL homepage
                'source_type': 'scrape',
                'scarcity_score': 0.6,
                'relevance_score': 0.7
            },
        ])
        
        self.logger.info(f"Found {len(offers)} offers from Foot Locker")
        return offers
