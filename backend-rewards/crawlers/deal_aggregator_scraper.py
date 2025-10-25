"""
Deal Aggregator Scraper - Scrapes actual deals from public deal aggregator sites.
This is used as a fallback for vendors that are difficult to scrape directly.
"""

from typing import List, Dict
from datetime import datetime, timedelta
from .base_crawler import BaseCrawler, CrawlerConfig
import re


class DealAggregatorScraper(BaseCrawler):
    """
    Scrapes actual deals from public deal aggregator sites like RetailMeNot, Slickdeals, etc.
    This provides real, up-to-date deals when direct vendor scraping is challenging.
    """
    
    def __init__(self, vendor_name: str, vendor_slug: str):
        """
        Initialize scraper for a specific vendor.
        
        Args:
            vendor_name: Display name of the vendor (e.g., "Amazon")
            vendor_slug: URL slug for the vendor (e.g., "amazon.com")
        """
        self.target_vendor = vendor_name
        self.vendor_slug = vendor_slug
        
        config = CrawlerConfig(
            vendor_name=vendor_name,
            base_url=f"https://www.retailmenot.com",
            rate_limit_seconds=2.0,
            use_playwright=False  # RetailMeNot works well with regular HTTP
        )
        super().__init__(config)
    
    async def crawl(self) -> List[Dict]:
        """Crawl actual deals from RetailMeNot for this vendor."""
        offers = []
        
        try:
            # RetailMeNot public page for vendor
            url = f"https://www.retailmenot.com/view/{self.vendor_slug}"
            
            html = await self.fetch_html(url)
            if not html:
                self.logger.warning(f"Could not fetch deals for {self.target_vendor}")
                return offers
            
            soup = self.parse_html(html)
            
            # Find deal cards/offers
            deal_items = soup.find_all(
                ['div', 'article', 'li'],
                class_=re.compile(r'offer|deal|coupon|promo', re.I),
                limit=15
            )
            
            for item in deal_items:
                try:
                    # Extract title/description
                    title_elem = item.find(['h2', 'h3', 'h4', 'p', 'span'], 
                                           class_=re.compile(r'title|description|offer-title', re.I))
                    
                    if not title_elem:
                        # Try data attributes
                        title_elem = item.find(attrs={'data-title': True})
                        if title_elem:
                            title = title_elem.get('data-title', '')
                        else:
                            continue
                    else:
                        title = title_elem.get_text(strip=True)
                    
                    if len(title) < 5 or len(title) > 150:
                        continue
                    
                    # Extract discount info
                    item_text = item.get_text()
                    
                    # Look for percentage off
                    percent_match = re.search(r'(\d+)%\s*off', item_text, re.I)
                    discount_percent = float(percent_match.group(1)) if percent_match else None
                    
                    # Look for dollar amounts (e.g., "$20 off", "Save $15")
                    dollar_match = re.search(r'\$(\d+(?:\.\d{2})?)\s*off', item_text, re.I)
                    dollar_value = float(dollar_match.group(1)) if dollar_match else None
                    
                    # Estimate value
                    if dollar_value:
                        estimated_value = dollar_value
                    elif discount_percent:
                        # Estimate based on typical purchase size
                        if discount_percent >= 50:
                            estimated_value = 30.0
                        elif discount_percent >= 25:
                            estimated_value = 20.0
                        elif discount_percent >= 10:
                            estimated_value = 10.0
                        else:
                            estimated_value = 5.0
                    else:
                        estimated_value = 5.0  # Free shipping, etc.
                    
                    # Look for expiry
                    expiry_elem = item.find(text=re.compile(r'exp|ends', re.I))
                    expiry = None
                    if expiry_elem:
                        # Try to extract date
                        date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', str(expiry_elem))
                        if date_match:
                            try:
                                month, day, year = date_match.groups()
                                year = int(year)
                                if year < 100:
                                    year += 2000
                                expiry = datetime(year, int(month), int(day))
                            except:
                                expiry = datetime.now() + timedelta(days=30)
                        else:
                            expiry = datetime.now() + timedelta(days=14)  # Default 2 weeks
                    
                    # Extract promo code if present
                    code_elem = item.find(class_=re.compile(r'code|coupon', re.I))
                    promo_code = None
                    if code_elem:
                        code_text = code_elem.get_text(strip=True)
                        code_match = re.search(r'^([A-Z0-9]{4,})$', code_text, re.I)
                        if code_match:
                            promo_code = code_match.group(1)
                    
                    # Build offer title
                    offer_title = title
                    if promo_code and promo_code not in title:
                        offer_title = f"{title} (Code: {promo_code})"
                    
                    # Extract link
                    link_elem = item.find('a', href=True)
                    offer_url = link_elem['href'] if link_elem else url
                    
                    # If it's a relative URL or tracking URL, try to get the actual vendor URL
                    if 'goto' in offer_url or 'out' in offer_url:
                        # This is a tracking link, extract the actual URL if possible
                        actual_url_match = re.search(r'url=([^&]+)', offer_url)
                        if actual_url_match:
                            import urllib.parse
                            offer_url = urllib.parse.unquote(actual_url_match.group(1))
                    
                    if not offer_url.startswith('http'):
                        offer_url = f"https://www.retailmenot.com{offer_url}"
                    
                    # Categorize based on vendor
                    categories = self._categorize_vendor(self.target_vendor)
                    
                    # Add offer
                    offers.append({
                        'title': offer_title[:120],
                        'expiry': expiry,
                        'discount_percent': discount_percent,
                        'estimated_value': estimated_value,
                        'categories': categories,
                        'terms': promo_code if promo_code else 'Check site for details.',
                        'url': offer_url,
                        'source_type': 'scrape',
                        'scarcity_score': 0.6,  # Publicly available deals
                        'relevance_score': 0.7
                    })
                    
                except Exception as e:
                    self.logger.debug(f"Error parsing deal item: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error scraping deals for {self.target_vendor}: {e}")
        
        self.logger.info(f"Found {len(offers)} real offers for {self.target_vendor}")
        return offers
    
    def _categorize_vendor(self, vendor_name: str) -> List[str]:
        """Categorize vendor based on name."""
        vendor_lower = vendor_name.lower()
        
        categories = []
        
        if any(word in vendor_lower for word in ['doordash', 'uber', 'instacart', 'grubhub']):
            categories.extend(['Food', 'Delivery'])
        
        if any(word in vendor_lower for word in ['nike', 'adidas', 'footlocker', 'newbalance', 'stockx']):
            categories.extend(['Sneakers', 'Athletic', 'Fashion'])
        
        if any(word in vendor_lower for word in ['h&m', 'zara', 'gap', 'forever21']):
            categories.extend(['Fashion', 'Clothing'])
        
        if any(word in vendor_lower for word in ['amazon', 'walmart', 'target']):
            categories.extend(['Shopping', 'Retail', 'General'])
        
        if any(word in vendor_lower for word in ['instacart', 'whole foods', 'grocery']):
            categories.extend(['Grocery', 'Food'])
        
        if not categories:
            categories = ['Shopping', 'General']
        
        return categories

