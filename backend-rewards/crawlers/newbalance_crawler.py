"""
New Balance crawler for athletic apparel and sneaker deals.
"""

from typing import List, Dict
from datetime import datetime, timedelta
from .base_crawler import BaseCrawler, CrawlerConfig


class NewBalanceCrawler(BaseCrawler):
    """Crawler for New Balance deals and offers."""
    
    def __init__(self):
        config = CrawlerConfig(
            vendor_name="New Balance",
            base_url="https://www.newbalance.com",
            rate_limit_seconds=1.5
        )
        super().__init__(config)
    
    async def crawl(self) -> List[Dict]:
        """Crawl New Balance deals."""
        offers = []
        
        mock_offers = [
            {
                'title': '25% Off Sitewide',
                'expiry': datetime.now() + timedelta(days=7),
                'discount_percent': 25.0,
                'estimated_value': 25.0,
                'categories': ['Sneakers', 'Athletic', 'Fashion'],
                'terms': 'Use code: SAVE25. Excludes new releases.',
                'url': 'https://www.newbalance.com/sale/',
                'source_type': 'scrape',
                'scarcity_score': 0.65,
                'relevance_score': 0.75
            },
            {
                'title': 'Up to 50% Off Sale Styles',
                'expiry': datetime.now() + timedelta(days=14),
                'discount_percent': 50.0,
                'estimated_value': 50.0,
                'categories': ['Sneakers', 'Athletic', 'Fashion', 'Sale'],
                'terms': 'Select styles. Limited sizes.',
                'url': 'https://www.newbalance.com/sale/',
                'source_type': 'scrape',
                'scarcity_score': 0.7,
                'relevance_score': 0.8
            },
            {
                'title': 'Free Shipping on Orders Over $50',
                'expiry': None,
                'discount_percent': None,
                'estimated_value': 7.0,
                'categories': ['Sneakers', 'Athletic', 'Fashion'],
                'terms': 'Standard shipping. All orders.',
                'url': 'https://www.newbalance.com/customer-service/shipping-policy.html',
                'source_type': 'api',
                'scarcity_score': 0.2,
                'relevance_score': 0.5
            },
            {
                'title': 'Extra 10% Off for Email Signup',
                'expiry': None,
                'discount_percent': 10.0,
                'estimated_value': 10.0,
                'categories': ['Sneakers', 'Athletic', 'Fashion'],
                'terms': 'New subscribers only. First purchase.',
                'url': 'https://www.newbalance.com/',
                'source_type': 'api',
                'scarcity_score': 0.4,
                'relevance_score': 0.65
            },
            {
                'title': 'Buy 2, Get 20% Off',
                'expiry': datetime.now() + timedelta(days=10),
                'discount_percent': 20.0,
                'estimated_value': 20.0,
                'categories': ['Sneakers', 'Athletic', 'Fashion'],
                'terms': 'Automatically applied at checkout. Mix and match.',
                'url': 'https://www.newbalance.com/deals/',
                'source_type': 'scrape',
                'scarcity_score': 0.6,
                'relevance_score': 0.7
            },
        ]
        
        offers.extend(mock_offers)
        
        self.logger.info(f"Found {len(offers)} offers from New Balance")
        return offers

