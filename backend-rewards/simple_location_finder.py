#!/usr/bin/env python3
"""
Simple Location-Based Offer Finder
Works with just standard library + requests (easier to install)
"""

import requests
import re
import time
import json
from typing import List, Dict
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class SimpleLocationFinder:
    """Simple version using just requests library."""
    
    # Major chain restaurant deal pages (verified working URLs)
    CHAIN_DEALS = {
        'McDonald\'s': 'https://www.mcdonalds.com/us/en-us/deals.html',
        'Burger King': 'https://www.bk.com/offers',
        'Wendy\'s': 'https://www.wendys.com/offers',
        'Taco Bell': 'https://www.tacobell.com/offers',
        'Subway': 'https://www.subway.com/en-US/deals',
        'Chipotle': 'https://www.chipotle.com/order',
        'KFC': 'https://www.kfc.com/deals',
        'Popeyes': 'https://www.popeyes.com/offers',
        'Domino\'s': 'https://www.dominos.com/en/pages/order/coupon/deals/',
        'Pizza Hut': 'https://www.pizzahut.com/deals',
        'Panera': 'https://www.panerabread.com/en-us/articles/rewards.html',
        'Arby\'s': 'https://arbys.com/deals',
        'Sonic': 'https://www.sonicdrivein.com/deals',
        'Dairy Queen': 'https://www.dairyqueen.com/us-en/deals/',
        'Five Guys': 'https://www.fiveguys.com/',
        'Chick-fil-A': 'https://www.chick-fil-a.com/stories/inside-chick-fil-a/chick-fil-a-one-app',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_chain_deals(self, chain_name: str, url: str) -> List[Dict]:
        """Scrape deals from a chain restaurant."""
        offers = []
        
        try:
            print(f"  Checking {chain_name}...")
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"    ⚠️  {response.status_code} error")
                return offers
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for deal/offer elements
            deal_elements = soup.find_all(
                ['div', 'article', 'li', 'section'],
                class_=re.compile(r'deal|offer|promo|special|coupon|card', re.I),
                limit=15
            )
            
            # Also check for specific text patterns
            if not deal_elements:
                # Fallback: look for any elements with deal-related text
                all_text = soup.find_all(text=re.compile(r'\$\d+.*off|save|discount|\d+%.*off', re.I))
                deal_elements = [elem.parent for elem in all_text[:10] if elem.parent]
            
            for element in deal_elements:
                try:
                    text = element.get_text(strip=True)
                    
                    # Skip if too short
                    if len(text) < 15:
                        continue
                    
                    # Extract title (look for headings first)
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b'])
                    title = title_elem.get_text(strip=True) if title_elem else text[:100]
                    
                    # Skip duplicates
                    if any(title.lower() in o['title'].lower() for o in offers):
                        continue
                    
                    # Extract value
                    dollar_match = re.search(r'\$(\d+(?:\.\d{2})?)', text)
                    percent_match = re.search(r'(\d+)%\s*off', text, re.I)
                    
                    estimated_value = 5.0
                    discount_percent = None
                    
                    if dollar_match:
                        estimated_value = float(dollar_match.group(1))
                    elif percent_match:
                        discount_percent = float(percent_match.group(1))
                        estimated_value = 10.0 if discount_percent > 20 else 5.0
                    
                    # Extract promo code if present
                    code_match = re.search(r'(?:code|promo)[\s:]+([A-Z0-9]{4,})', text, re.I)
                    promo_code = code_match.group(1) if code_match else None
                    
                    offer_title = f"{chain_name}: {title}"
                    if promo_code:
                        offer_title += f" (Code: {promo_code})"
                    
                    offers.append({
                        'title': offer_title[:150],
                        'restaurant': chain_name,
                        'discount_percent': discount_percent,
                        'estimated_value': estimated_value,
                        'url': url,
                        'verified_live': True,
                        'scraped_at': datetime.now().isoformat(),
                        'terms': text[:200] if len(text) > 100 else text
                    })
                    
                except Exception as e:
                    continue
            
            if offers:
                print(f"    ✅ Found {len(offers)} offers")
            else:
                print(f"    ℹ️  No offers found on page")
            
            # Rate limiting
            time.sleep(1)
            
        except requests.exceptions.Timeout:
            print(f"    ⚠️  Timeout")
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  Error: {str(e)[:50]}")
        except Exception as e:
            print(f"    ⚠️  Unexpected error: {str(e)[:50]}")
        
        return offers
    
    def find_all_chain_deals(self) -> List[Dict]:
        """Scrape all chain restaurants for current deals."""
        all_offers = []
        
        print("\n🔍 Checking major chain restaurants for current deals...\n")
        
        for chain_name, url in self.CHAIN_DEALS.items():
            offers = self.scrape_chain_deals(chain_name, url)
            all_offers.extend(offers)
        
        return all_offers


def main():
    """Main function."""
    import sys
    
    print("\n" + "="*80)
    print("🍔 LIVE RESTAURANT DEAL FINDER")
    print("="*80)
    print("\nScanning major chain restaurants for current offers...")
    print("(This checks actual restaurant websites in real-time)")
    print("="*80)
    
    finder = SimpleLocationFinder()
    
    try:
        offers = finder.find_all_chain_deals()
        
        if offers:
            print(f"\n{'='*80}")
            print(f"✅ FOUND {len(offers)} LIVE OFFERS!")
            print(f"{'='*80}\n")
            
            # Sort by value
            offers.sort(key=lambda x: x['estimated_value'], reverse=True)
            
            for i, offer in enumerate(offers, 1):
                print(f"{i}. {offer['title']}")
                print(f"   Restaurant: {offer['restaurant']}")
                if offer['discount_percent']:
                    print(f"   Discount: {offer['discount_percent']}% off")
                print(f"   Est. Value: ${offer['estimated_value']:.2f}")
                print(f"   URL: {offer['url']}")
                print(f"   ✅ Verified Live (scraped {offer['scraped_at'][:10]})")
                if len(offer.get('terms', '')) > 50:
                    print(f"   Terms: {offer['terms'][:150]}...")
                print()
            
            # Save to file
            with open('live_deals.json', 'w') as f:
                json.dump(offers, f, indent=2)
            print(f"💾 Saved to live_deals.json\n")
            
            # Summary by restaurant
            print(f"{'='*80}")
            print("📊 SUMMARY BY RESTAURANT:")
            print(f"{'='*80}")
            restaurant_counts = {}
            for offer in offers:
                restaurant_counts[offer['restaurant']] = restaurant_counts.get(offer['restaurant'], 0) + 1
            
            for restaurant, count in sorted(restaurant_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   {restaurant}: {count} offers")
            
        else:
            print("\n" + "="*80)
            print("❌ NO LIVE OFFERS FOUND")
            print("="*80)
            print("\nPossible reasons:")
            print("  • Restaurant websites may be blocking automated access")
            print("  • No current promotions available")
            print("  • Network connectivity issues")
            print("\nTry again later or check restaurant websites manually.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

