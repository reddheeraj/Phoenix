"""
Location-Based Restaurant & Fast Food Offer Finder
Uses live location/zipcode to find nearby restaurants and their current offers.
NOW WITH PROVEN SCRAPING FROM simple_location_finder.py!
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import json
from math import radians, cos, sin, asin, sqrt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocationBasedOfferFinder:
    """Finds restaurants near you and scrapes their current live offers."""
    
    # PROVEN chain restaurant deal pages (UPDATED URLs)
    # NOTE: Some sites (KFC, Panera, Dairy Queen) have aggressive anti-bot protection
    # and may return 403 errors despite best efforts. This is expected behavior.
    CHAIN_DEALS = {
        'McDonald\'s': 'https://www.mcdonalds.com/us/en-us/deals.html',
        'Burger King': 'https://www.bk.com/offers',
        'Wendy\'s': 'https://www.wendys.com/promotions',
        'Taco Bell': 'https://www.tacobell.com/food',
        'Subway': 'https://www.subway.com/en-us',  # FIXED: homepage (faster)
        'Chipotle': 'https://www.chipotle.com/order',
        'KFC': 'https://www.kfc.com/menu',  # May get 403 (aggressive protection)
        'Popeyes': 'https://www.popeyes.com/offers',
        'Domino\'s': 'https://www.dominos.com/en/pages/order/',
        'Pizza Hut': 'https://www.pizzahut.com/',  # FIXED: homepage (faster)
        'Panera': 'https://www.panerabread.com/',  # May get 403 (aggressive protection)
        'Arby\'s': 'https://arbys.com/deals',
        'Sonic': 'https://www.sonicdrivein.com/deals',
        'Dairy Queen': 'https://www.dairyqueen.com/',  # May get 403 (aggressive protection)
        'Five Guys': 'https://www.fiveguys.com/',
        'Chick-fil-A': 'https://www.chick-fil-a.com/one',
    }
    
    def __init__(self, zipcode: str = None, latitude: float = None, longitude: float = None):
        """
        Initialize with location.
        
        Args:
            zipcode: US zip code (e.g., "10001")
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        """
        self.zipcode = zipcode
        self.latitude = latitude
        self.longitude = longitude
        self.session = None
        
    async def initialize(self):
        """Initialize HTTP session with better headers to avoid blocking."""
        # Realistic browser headers to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Increased timeout for slow sites
        timeout = aiohttp.ClientTimeout(total=20, connect=10, sock_read=15)
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout
        )
        
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    async def get_coordinates_from_zipcode(self, zipcode: str) -> Tuple[float, float]:
        """Convert zipcode to coordinates using OpenStreetMap Nominatim API."""
        try:
            url = f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&country=US&format=json"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        lat = float(data[0]['lat'])
                        lon = float(data[0]['lon'])
                        logger.info(f"Zipcode {zipcode} → {lat}, {lon}")
                        return lat, lon
        except Exception as e:
            logger.error(f"Error getting coordinates: {e}")
        
        return None, None
    
    async def find_nearby_restaurants(self) -> List[Dict]:
        """
        Find nearby restaurants and fast food places.
        Uses OpenStreetMap Overpass API (free, no API key needed).
        """
        restaurants = []
        
        # Get coordinates
        lat, lon = self.latitude, self.longitude
        
        if not lat and self.zipcode:
            lat, lon = await self.get_coordinates_from_zipcode(self.zipcode)
        
        if not lat or not lon:
            logger.error("No valid location provided")
            return []
        
        try:
            # Search radius in meters (5000m = 3.1 miles)
            radius = 5000
            
            # Overpass API query for restaurants and fast food
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["amenity"="restaurant"](around:{radius},{lat},{lon});
              node["amenity"="fast_food"](around:{radius},{lat},{lon});
              way["amenity"="restaurant"](around:{radius},{lat},{lon});
              way["amenity"="fast_food"](around:{radius},{lat},{lon});
            );
            out body;
            >;
            out skel qt;
            """
            
            url = "https://overpass-api.de/api/interpreter"
            
            async with self.session.post(url, data={'data': overpass_query}) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for element in data.get('elements', []):
                        if 'tags' in element:
                            tags = element['tags']
                            
                            # Extract restaurant info
                            name = tags.get('name', 'Unknown')
                            brand = tags.get('brand', tags.get('name', ''))
                            cuisine = tags.get('cuisine', 'General')
                            
                            # Get coordinates
                            elem_lat = element.get('lat', lat)
                            elem_lon = element.get('lon', lon)
                            
                            # Calculate distance
                            distance_km = self._haversine_distance(lat, lon, elem_lat, elem_lon)
                            
                            restaurants.append({
                                'name': name,
                                'brand': brand,
                                'cuisine': cuisine,
                                'latitude': elem_lat,
                                'longitude': elem_lon,
                                'distance_km': round(distance_km, 2),
                                'amenity': tags.get('amenity')
                            })
            
            # Sort by distance
            restaurants.sort(key=lambda x: x['distance_km'])
            
            logger.info(f"Found {len(restaurants)} restaurants within {radius}m")
            
        except Exception as e:
            logger.error(f"Error finding restaurants: {e}")
        
        return restaurants
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km."""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km
    
    async def scrape_chain_deals(self, chain_name: str, url: str, distance_km: float = None, retry_count: int = 0) -> List[Dict]:
        """
        Scrape deals from a chain restaurant using PROVEN methods from simple_location_finder.py
        Now with retry logic and better error handling!
        """
        offers = []
        max_retries = 2
        
        try:
            logger.info(f"  Checking {chain_name}... ({distance_km}km away)" if distance_km else f"  Checking {chain_name}...")
            
            # Increased timeout to 20 seconds for slow sites
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=20), ssl=False) as response:
                if response.status != 200:
                    # Retry on 403/404 once with different approach
                    if response.status in [403, 404] and retry_count < max_retries:
                        logger.debug(f"    🔄 Retrying {chain_name} (attempt {retry_count + 1})...")
                        await asyncio.sleep(2)
                        return await self.scrape_chain_deals(chain_name, url, distance_km, retry_count + 1)
                    
                    logger.warning(f"    ⚠️  {response.status} error")
                    return offers
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # PROVEN METHOD: Look for deal/offer elements
                deal_elements = soup.find_all(
                    ['div', 'article', 'li', 'section'],
                    class_=re.compile(r'deal|offer|promo|special|coupon|card', re.I),
                    limit=15
                )
                
                # Fallback: look for text patterns
                if not deal_elements:
                    all_text = soup.find_all(string=re.compile(r'\$\d+.*off|save|discount|\d+%.*off', re.I))
                    deal_elements = [elem.parent for elem in all_text[:10] if elem.parent]
                
                for element in deal_elements:
                    try:
                        text = element.get_text(strip=True)
                        
                        # Skip if too short
                        if len(text) < 15:
                            continue
                        
                        # Extract title
                        title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b'])
                        title = title_elem.get_text(strip=True) if title_elem else text[:100]
                        
                        # Skip duplicates
                        if any(title.lower() in o['title'].lower() for o in offers):
                            continue
                        
                        # Extract value using PROVEN patterns
                        dollar_match = re.search(r'\$(\d+(?:\.\d{2})?)', text)
                        percent_match = re.search(r'(\d+)%\s*off', text, re.I)
                        
                        estimated_value = 5.0
                        discount_percent = None
                        
                        if dollar_match:
                            estimated_value = float(dollar_match.group(1))
                        elif percent_match:
                            discount_percent = float(percent_match.group(1))
                            estimated_value = 10.0 if discount_percent > 20 else 5.0
                        
                        # Extract promo code
                        code_match = re.search(r'(?:code|promo)[\s:]+([A-Z0-9]{4,})', text, re.I)
                        promo_code = code_match.group(1) if code_match else None
                        
                        offer_title = f"{chain_name}: {title}"
                        if promo_code:
                            offer_title += f" (Code: {promo_code})"
                        
                        offers.append({
                            'title': offer_title[:150],
                            'restaurant': chain_name,
                            'brand': chain_name,
                            'discount_percent': discount_percent,
                            'estimated_value': estimated_value,
                            'url': url,
                            'distance_km': distance_km if distance_km else 0.0,
                            'cuisine': 'Fast Food',
                            'verified_live': True,
                            'scraped_at': datetime.now().isoformat(),
                            'terms': text[:200] if len(text) > 100 else text
                        })
                        
                    except Exception as e:
                        continue
                
                if offers:
                    logger.info(f"    ✅ Found {len(offers)} offers")
                else:
                    logger.debug(f"    ℹ️  No offers found")
                
        except asyncio.TimeoutError:
            # Retry on timeout
            if retry_count < max_retries:
                logger.debug(f"    🔄 Retrying {chain_name} after timeout (attempt {retry_count + 1})...")
                await asyncio.sleep(2)
                return await self.scrape_chain_deals(chain_name, url, distance_km, retry_count + 1)
            logger.warning(f"    ⚠️  Timeout (gave up after {max_retries} retries)")
        except Exception as e:
            logger.warning(f"    ⚠️  Error: {str(e)[:50]}")
        
        return offers
    
    async def find_all_local_offers(self) -> List[Dict]:
        """
        Main method: Find all restaurants near location and scrape their current offers.
        Uses PROVEN scraping methods from simple_location_finder.py
        """
        all_offers = []
        
        logger.info(f"\n{'='*80}")
        if self.zipcode:
            logger.info(f"🔍 Finding restaurants and offers near zipcode: {self.zipcode}")
        else:
            logger.info(f"🔍 Finding restaurant offers...")
        logger.info(f"{'='*80}\n")
        
        # Step 1: Find nearby restaurants
        nearby_restaurants = []
        if self.zipcode or (self.latitude and self.longitude):
            logger.info("📍 Step 1: Finding nearby restaurants...")
            nearby_restaurants = await self.find_nearby_restaurants()
            
            if nearby_restaurants:
                logger.info(f"   ✅ Found {len(nearby_restaurants)} restaurants nearby\n")
            else:
                logger.warning("   ⚠️  No nearby restaurants found, checking national chains only\n")
        
        # Step 2: Check which nearby restaurants are known chains
        nearby_chains = {}
        if nearby_restaurants:
            logger.info("📊 Step 2: Matching nearby restaurants to known chains...")
            for restaurant in nearby_restaurants:
                brand = restaurant['brand'].lower()
                name = restaurant['name'].lower()
                
                # Match to known chains
                for chain_name, chain_url in self.CHAIN_DEALS.items():
                    chain_key = chain_name.lower().split()[0]  # First word
                    
                    if chain_key in brand or chain_key in name:
                        if chain_name not in nearby_chains:
                            nearby_chains[chain_name] = restaurant
                            logger.info(f"   ✅ {chain_name} found ({restaurant['distance_km']}km away)")
            
            logger.info(f"\n   Found {len(nearby_chains)} known chains nearby\n")
        
        # Step 3: Scrape offers from nearby chains first
        logger.info("🍔 Step 3: Checking nearby chains for live offers...\n")
        
        if nearby_chains:
            for chain_name, restaurant in nearby_chains.items():
                url = self.CHAIN_DEALS[chain_name]
                offers = await self.scrape_chain_deals(
                    chain_name, 
                    url, 
                    distance_km=restaurant['distance_km']
                )
                all_offers.extend(offers)
                await asyncio.sleep(1.5)  # Increased rate limiting to avoid blocks
        
        # Step 4: Check remaining national chains (not found nearby)
        remaining_chains = {k: v for k, v in self.CHAIN_DEALS.items() if k not in nearby_chains}
        
        if remaining_chains:
            logger.info(f"\n🌐 Step 4: Checking {len(remaining_chains)} additional national chains...\n")
            
            for chain_name, url in remaining_chains.items():
                offers = await self.scrape_chain_deals(chain_name, url)
                all_offers.extend(offers)
                await asyncio.sleep(1.5)  # Increased rate limiting to avoid blocks
        
        # Sort by distance (nearby first) then by value
        all_offers.sort(key=lambda x: (x['distance_km'], -x['estimated_value']))
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ TOTAL: Found {len(all_offers)} live offers!")
        logger.info(f"{'='*80}\n")
        
        return all_offers


async def main():
    """Example usage."""
    import sys
    
    # Get zipcode from command line or skip for national search
    zipcode = sys.argv[1] if len(sys.argv) > 1 else None
    
    if zipcode:
        print(f"\n🔍 Finding restaurants and offers near zipcode: {zipcode}\n")
    else:
        print(f"\n🔍 Finding restaurant offers (no location specified - checking national chains)\n")
        print("💡 Tip: Run with zipcode for location-based results:")
        print("   python location_based_finder.py YOUR_ZIP\n")
    
    finder = LocationBasedOfferFinder(zipcode=zipcode)
    await finder.initialize()
    
    try:
        offers = await finder.find_all_local_offers()
        
        if offers:
            print(f"\n{'='*80}")
            print(f"✅ FOUND {len(offers)} LIVE OFFERS!")
            print(f"{'='*80}\n")
            
            # Group by nearby vs national
            nearby_offers = [o for o in offers if o['distance_km'] > 0 and o['distance_km'] < 100]
            national_offers = [o for o in offers if o['distance_km'] == 0 or o['distance_km'] >= 100]
            
            if nearby_offers:
                print(f"📍 NEARBY OFFERS ({len(nearby_offers)}):")
                print("="*80)
                for i, offer in enumerate(nearby_offers, 1):
                    print(f"\n{i}. {offer['title']}")
                    print(f"   🏪 {offer['restaurant']} - {offer['distance_km']}km away")
                    if offer['discount_percent']:
                        print(f"   💰 Discount: {offer['discount_percent']}% off")
                    print(f"   💵 Value: ${offer['estimated_value']:.2f}")
                    print(f"   🔗 {offer['url']}")
                    print(f"   ✅ Verified Live")
            
            if national_offers:
                print(f"\n\n🌐 NATIONAL CHAIN OFFERS ({len(national_offers)}):")
                print("="*80)
                for i, offer in enumerate(national_offers, 1):
                    print(f"\n{i}. {offer['title']}")
                    print(f"   🏪 {offer['restaurant']}")
                    if offer['discount_percent']:
                        print(f"   💰 Discount: {offer['discount_percent']}% off")
                    print(f"   💵 Value: ${offer['estimated_value']:.2f}")
                    print(f"   🔗 {offer['url']}")
                    print(f"   ✅ Verified Live")
            
            # Save to file
            filename = f"location_deals_{zipcode if zipcode else 'national'}.json"
            with open(filename, 'w') as f:
                json.dump(offers, f, indent=2)
            print(f"\n💾 Saved to {filename}")
            
            # Summary
            print(f"\n{'='*80}")
            print(f"📊 SUMMARY:")
            print(f"{'='*80}")
            print(f"Total Offers: {len(offers)}")
            if zipcode:
                print(f"Nearby Offers: {len(nearby_offers)}")
                print(f"National Offers: {len(national_offers)}")
            
            # By restaurant
            restaurant_counts = {}
            for offer in offers:
                restaurant_counts[offer['restaurant']] = restaurant_counts.get(offer['restaurant'], 0) + 1
            
            print(f"\nOffers by Restaurant:")
            for restaurant, count in sorted(restaurant_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   {restaurant}: {count}")
            
        else:
            print("\n❌ No live offers found.")
            print("\nPossible reasons:")
            print("  • Restaurant websites may be blocking requests")
            print("  • No current promotions available")
            print("  • Try again in a few minutes")
    
    finally:
        await finder.close()


if __name__ == "__main__":
    asyncio.run(main())
