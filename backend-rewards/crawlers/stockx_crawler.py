"""
StockX crawler for sneaker marketplace deals.
"""

from typing import List, Dict
from datetime import datetime, timedelta
from .base_crawler import BaseCrawler, CrawlerConfig


class StockXCrawler(BaseCrawler):
    """Crawler for StockX deals and offers."""
    
    def __init__(self):
        config = CrawlerConfig(
            vendor_name="StockX",
            base_url="https://stockx.com",
            rate_limit_seconds=2.0
        )
        super().__init__(config)
    
    async def crawl(self) -> List[Dict]:
        """Crawl StockX deals."""
        offers = []
        
        mock_offers = [
            {
                'title': '$25 Off First Purchase',
                'expiry': datetime.now() + timedelta(days=30),
                'discount_percent': None,
                'estimated_value': 25.0,
                'categories': ['Sneakers', 'Streetwear', 'Collectibles'],
                'terms': 'New users only. Min purchase $250. Use referral code.',
                'url': 'https://stockx.com/promo',
                'source_type': 'api',
                'scarcity_score': 0.5,
                'relevance_score': 0.8
            },
            {
                'title': 'Free Shipping on Orders Over $150',
                'expiry': datetime.now() + timedelta(days=14),
                'discount_percent': None,
                'estimated_value': 13.95,
                'categories': ['Sneakers', 'Streetwear', 'Collectibles'],
                'terms': 'Limited time. Standard shipping.',
                'url': 'https://stockx.com/shipping',
                'source_type': 'scrape',
                'scarcity_score': 0.6,
                'relevance_score': 0.65
            },
            {
                'title': 'Reduced Seller Fees - 8.5% (Usually 9.5%)',
                'expiry': datetime.now() + timedelta(days=7),
                'discount_percent': 10.5,  # Relative reduction
                'estimated_value': 10.0,
                'categories': ['Sneakers', 'Streetwear'],
                'terms': 'For sellers. Limited time promotion.',
                'url': 'https://stockx.com/sell',
                'source_type': 'api',
                'scarcity_score': 0.7,
                'relevance_score': 0.6
            },
        ]
        
        offers.extend(mock_offers)
        
        self.logger.info(f"Found {len(offers)} offers from StockX")
        return offers

