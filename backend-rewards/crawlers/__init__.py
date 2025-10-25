"""
Modular web crawler package for different vendors.
Each vendor has its own crawler module.
"""

from .base_crawler import BaseCrawler, CrawlerConfig
from .deal_aggregator_scraper import DealAggregatorScraper
from .amazon_crawler import AmazonCrawler
from .instacart_crawler import InstacartCrawler
from .uber_eats_crawler import UberEatsCrawler
from .doordash_crawler import DoorDashCrawler
from .hm_crawler import HMCrawler
from .zara_crawler import ZaraCrawler
from .footlocker_crawler import FootLockerCrawler
from .stockx_crawler import StockXCrawler
from .studentbeans_crawler import StudentBeansCrawler
from .nike_crawler import NikeCrawler
from .newbalance_crawler import NewBalanceCrawler

__all__ = [
    'BaseCrawler',
    'CrawlerConfig',
    'DealAggregatorScraper',
    'AmazonCrawler',
    'InstacartCrawler',
    'UberEatsCrawler',
    'DoorDashCrawler',
    'HMCrawler',
    'ZaraCrawler',
    'FootLockerCrawler',
    'StockXCrawler',
    'StudentBeansCrawler',
    'NikeCrawler',
    'NewBalanceCrawler',
]

