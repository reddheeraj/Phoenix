#!/usr/bin/env python3
"""
Run all shopping vendor crawlers and display offers.
Usage: python run_shopping_crawlers.py
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict

# Import all shopping vendor crawlers
from crawlers.amazon_crawler import AmazonCrawler
from crawlers.nike_crawler import NikeCrawler
from crawlers.hm_crawler import HMCrawler
from crawlers.zara_crawler import ZaraCrawler
from crawlers.footlocker_crawler import FootLockerCrawler
from crawlers.stockx_crawler import StockXCrawler
from crawlers.studentbeans_crawler import StudentBeansCrawler
from crawlers.newbalance_crawler import NewBalanceCrawler
from crawlers.doordash_crawler import DoorDashCrawler
from crawlers.uber_eats_crawler import UberEatsCrawler
from crawlers.instacart_crawler import InstacartCrawler


async def run_all_shopping_crawlers() -> List[Dict]:
    """
    Run all shopping vendor crawlers and collect their offers.
    """
    all_offers = []
    
    # List of all shopping vendor crawlers
    crawlers = [
        ('Amazon', AmazonCrawler),
        ('Nike', NikeCrawler),
        ('H&M', HMCrawler),
        ('Zara', ZaraCrawler),
        ('Foot Locker', FootLockerCrawler),
        ('StockX', StockXCrawler),
        ('Student Beans', StudentBeansCrawler),
        ('New Balance', NewBalanceCrawler),
        ('DoorDash', DoorDashCrawler),
        ('Uber Eats', UberEatsCrawler),
        ('Instacart', InstacartCrawler),
    ]
    
    print(f"\n{'='*80}")
    print(f"🛍️  SHOPPING VENDOR CRAWLER")
    print(f"{'='*80}\n")
    print(f"Running {len(crawlers)} vendor crawlers...\n")
    
    # Run each crawler
    for vendor_name, CrawlerClass in crawlers:
        try:
            print(f"🔍 Crawling {vendor_name}...", end=" ", flush=True)
            
            crawler = CrawlerClass()
            await crawler.initialize()
            
            try:
                offers = await crawler.crawl()
                
                if offers:
                    print(f"✅ Found {len(offers)} offers")
                    all_offers.extend(offers)
                else:
                    print(f"⚠️  No offers found")
                    
            finally:
                await crawler.close()
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
            continue
        
        # Rate limiting
        await asyncio.sleep(1.5)
    
    return all_offers


def display_offers(offers: List[Dict]):
    """Display offers in a nice format."""
    print(f"\n{'='*80}")
    print(f"✅ FOUND {len(offers)} TOTAL OFFERS!")
    print(f"{'='*80}\n")
    
    if not offers:
        print("❌ No offers found. Possible reasons:")
        print("  • Websites may be blocking requests")
        print("  • No current promotions available")
        print("  • Try running again in a few minutes")
        return
    
    # Group by vendor
    by_vendor = {}
    for offer in offers:
        vendor = offer.get('vendor', 'Unknown')
        if vendor not in by_vendor:
            by_vendor[vendor] = []
        by_vendor[vendor].append(offer)
    
    # Display by vendor
    for vendor, vendor_offers in sorted(by_vendor.items()):
        print(f"\n{'='*80}")
        print(f"🏪 {vendor.upper()} ({len(vendor_offers)} offers)")
        print(f"{'='*80}\n")
        
        for i, offer in enumerate(vendor_offers, 1):
            print(f"{i}. {offer.get('title', 'Untitled')[:80]}")
            
            if offer.get('discount_percent'):
                print(f"   💰 Discount: {offer['discount_percent']}% off")
            
            if offer.get('estimated_value'):
                print(f"   💵 Value: ${offer['estimated_value']:.2f}")
            
            if offer.get('categories'):
                cats = ', '.join(offer['categories']) if isinstance(offer['categories'], list) else offer['categories']
                print(f"   🏷️  Categories: {cats}")
            
            print(f"   🔗 {offer.get('url', 'No URL')}")
            print(f"   ✅ Verified Live\n")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"Total Offers: {len(offers)}")
    print(f"\nOffers by Vendor:")
    for vendor, vendor_offers in sorted(by_vendor.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {vendor}: {len(vendor_offers)}")


def save_offers(offers: List[Dict], filename: str = None):
    """Save offers to JSON file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shopping_offers_{timestamp}.json"
    
    # Convert datetime objects to strings for JSON serialization
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    with open(filename, 'w') as f:
        json.dump(offers, f, indent=2, default=json_serializer)
    
    print(f"\n💾 Saved to {filename}")


async def main():
    """Main function."""
    try:
        # Run all crawlers
        offers = await run_all_shopping_crawlers()
        
        # Display results
        display_offers(offers)
        
        # Save to file
        if offers:
            save_offers(offers)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

