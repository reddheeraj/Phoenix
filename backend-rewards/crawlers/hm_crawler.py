"""
H&M crawler for fashion deals.
"""

from typing import List, Dict
from datetime import datetime, timedelta
from .base_crawler import BaseCrawler, CrawlerConfig


class HMCrawler(BaseCrawler):
    """Crawler for H&M deals and offers."""
    
    def __init__(self):
        config = CrawlerConfig(
            vendor_name="H&M",
            base_url="https://www2.hm.com",
            rate_limit_seconds=1.5
        )
        super().__init__(config)
    
    async def crawl(self) -> List[Dict]:
        """Crawl H&M deals."""
        offers = []
        
        mock_offers = [
            {
                'title': '15% Off Student Discount',
                'expiry': None,  # Ongoing program
                'discount_percent': 15.0,
                'estimated_value': 15.0,  # Based on $100 purchase
                'categories': ['Fashion', 'Clothing', 'Student'],
                'terms': 'Verify student status. Valid in-store and online. Excludes sale items.',
                'url': 'https://www2.hm.com/en_us/student-discount.html',
                'source_type': 'api',
                'scarcity_score': 0.3,
                'relevance_score': 0.8
            },
            {
                'title': 'Up to 70% Off Sale Items',
                'expiry': datetime.now() + timedelta(days=14),
                'discount_percent': 70.0,
                'estimated_value': 35.0,
                'categories': ['Fashion', 'Clothing', 'Sale'],
                'terms': 'End of season sale. While supplies last.',
                'url': 'https://www2.hm.com/en_us/sale.html',
                'source_type': 'scrape',
                'scarcity_score': 0.7,
                'relevance_score': 0.7
            },
            {
                'title': '$10 Off $40+ Purchase',
                'expiry': datetime.now() + timedelta(days=10),
                'discount_percent': 25.0,
                'estimated_value': 10.0,
                'categories': ['Fashion', 'Clothing'],
                'terms': 'Members only. Use code: SAVE10',
                'url': 'https://www2.hm.com/en_us/member.html',
                'source_type': 'scrape',
                'scarcity_score': 0.6,
                'relevance_score': 0.65
            },
            {
                'title': 'Free Shipping on Orders Over $40',
                'expiry': None,
                'discount_percent': None,
                'estimated_value': 5.99,
                'categories': ['Fashion', 'Clothing'],
                'terms': 'Standard shipping. No code needed.',
                'url': 'https://www2.hm.com/en_us/customer-service/shipping.html',
                'source_type': 'api',
                'scarcity_score': 0.2,
                'relevance_score': 0.5
            },
        ]
        
        offers.extend(mock_offers)
        
        self.logger.info(f"Found {len(offers)} offers from H&M")
        return offers

