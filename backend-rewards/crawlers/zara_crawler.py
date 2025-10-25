"""
Zara crawler for fashion deals.
"""

from typing import List, Dict
from datetime import datetime, timedelta
from .base_crawler import BaseCrawler, CrawlerConfig


class ZaraCrawler(BaseCrawler):
    """Crawler for Zara deals and offers."""
    
    def __init__(self):
        config = CrawlerConfig(
            vendor_name="Zara",
            base_url="https://www.zara.com",
            rate_limit_seconds=1.5
        )
        super().__init__(config)
    
    async def crawl(self) -> List[Dict]:
        """Crawl Zara deals."""
        offers = []
        
        mock_offers = [
            {
                'title': 'Up to 50% Off Sale Collection',
                'expiry': datetime.now() + timedelta(days=21),
                'discount_percent': 50.0,
                'estimated_value': 40.0,
                'categories': ['Fashion', 'Clothing', 'Sale'],
                'terms': 'End of season sale. Select styles.',
                'url': 'https://www.zara.com/us/en/sale',
                'source_type': 'scrape',
                'scarcity_score': 0.65,
                'relevance_score': 0.7
            },
            {
                'title': 'Free Shipping on All Orders',
                'expiry': datetime.now() + timedelta(days=7),
                'discount_percent': None,
                'estimated_value': 4.95,
                'categories': ['Fashion', 'Clothing'],
                'terms': 'Limited time offer. All orders.',
                'url': 'https://www.zara.com/us/en/',
                'source_type': 'scrape',
                'scarcity_score': 0.7,
                'relevance_score': 0.6
            },
            {
                'title': 'New Arrivals - Special Launch Prices',
                'expiry': datetime.now() + timedelta(days=5),
                'discount_percent': 20.0,
                'estimated_value': 20.0,
                'categories': ['Fashion', 'Clothing', 'New'],
                'terms': 'New collection launch. Limited quantity.',
                'url': 'https://www.zara.com/us/en/new',
                'source_type': 'scrape',
                'scarcity_score': 0.8,
                'relevance_score': 0.65
            },
        ]
        
        offers.extend(mock_offers)
        
        self.logger.info(f"Found {len(offers)} offers from Zara")
        return offers

