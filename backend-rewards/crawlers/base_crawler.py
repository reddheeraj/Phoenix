"""
Base crawler class that all vendor-specific crawlers inherit from.
Handles robots.txt checking and common scraping functionality.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
import urllib.robotparser
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import time
import random
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    Browser = None
    Page = None


@dataclass
class CrawlerConfig:
    """Configuration for crawler behavior."""
    vendor_name: str
    base_url: str
    respect_robots_txt: bool = True
    rate_limit_seconds: float = 1.0  # Minimum delay between requests
    user_agent: str = "RewardAggregatorBot/1.0 (Educational Project)"
    timeout_seconds: int = 30
    max_retries: int = 3
    use_playwright: bool = False  # Use Playwright for JavaScript-heavy sites


class BaseCrawler(ABC):
    """Base class for all vendor-specific crawlers."""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self.last_request_time = 0
        self.session: Optional[aiohttp.ClientSession] = None
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def initialize(self):
        """Initialize crawler, check robots.txt."""
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': self.config.user_agent},
            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        )
        
        # Initialize Playwright if needed
        if self.config.use_playwright and PLAYWRIGHT_AVAILABLE:
            try:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=True)
                self.page = await self.browser.new_page(
                    user_agent=self.config.user_agent
                )
                self.logger.info(f"Playwright initialized for {self.config.vendor_name}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Playwright: {e}. Falling back to aiohttp.")
                self.config.use_playwright = False
        
        if self.config.respect_robots_txt:
            await self._check_robots_txt()
    
    async def _check_robots_txt(self):
        """Check and parse robots.txt file."""
        try:
            robots_url = urljoin(self.config.base_url, '/robots.txt')
            self.logger.info(f"Checking robots.txt at {robots_url}")
            
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_txt = await response.text()
                    self.robot_parser.parse(robots_txt.splitlines())
                    self.logger.info(f"Parsed robots.txt for {self.config.vendor_name}")
                else:
                    self.logger.warning(f"No robots.txt found for {self.config.vendor_name}")
        except Exception as e:
            self.logger.warning(f"Error checking robots.txt: {e}")
    
    def can_fetch(self, url: str) -> bool:
        """Check if URL can be crawled according to robots.txt."""
        if not self.config.respect_robots_txt:
            return True
        
        if not self.robot_parser.entries:
            return True  # No robots.txt means allowed
        
        return self.robot_parser.can_fetch(self.config.user_agent, url)
    
    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.config.rate_limit_seconds:
            delay = self.config.rate_limit_seconds - elapsed
            # Add small random jitter to avoid patterns
            delay += random.uniform(0, 0.5)
            await asyncio.sleep(delay)
        self.last_request_time = time.time()
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL with rate limiting and robots.txt check."""
        if not self.can_fetch(url):
            self.logger.warning(f"Blocked by robots.txt: {url}")
            return None
        
        await self._rate_limit()
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.info(f"Fetching {url} (attempt {attempt + 1})")
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        self.logger.warning(f"HTTP {response.status} for {url}")
                        if response.status == 429:  # Too Many Requests
                            await asyncio.sleep(5 * (attempt + 1))  # Exponential backoff
                        elif response.status >= 400:
                            return None  # Don't retry client errors
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout fetching {url}")
            except Exception as e:
                self.logger.error(f"Error fetching {url}: {e}")
            
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    async def fetch_json(self, url: str) -> Optional[Dict]:
        """Fetch JSON data from URL."""
        if not self.can_fetch(url):
            self.logger.warning(f"Blocked by robots.txt: {url}")
            return None
        
        await self._rate_limit()
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.info(f"Fetching JSON from {url} (attempt {attempt + 1})")
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.warning(f"HTTP {response.status} for {url}")
            except Exception as e:
                self.logger.error(f"Error fetching JSON from {url}: {e}")
            
            if attempt < self.config.max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup."""
        return BeautifulSoup(html, 'html.parser')
    
    async def fetch_with_playwright(self, url: str, wait_for: Optional[str] = None) -> Optional[str]:
        """
        Fetch page content using Playwright for JavaScript-rendered sites.
        
        Args:
            url: URL to fetch
            wait_for: CSS selector to wait for before extracting content
        """
        if not self.config.use_playwright or not self.page:
            self.logger.warning("Playwright not available, falling back to aiohttp")
            return await self.fetch_html(url)
        
        if not self.can_fetch(url):
            self.logger.warning(f"Blocked by robots.txt: {url}")
            return None
        
        await self._rate_limit()
        
        try:
            # Check if browser is closed and reinitialize if needed
            if self.browser is None or not self.browser.is_connected():
                self.logger.debug("Reinitializing Playwright browser...")
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=True)
                self.page = await self.browser.new_page()
            
            self.logger.info(f"Fetching with Playwright: {url}")
            await self.page.goto(url, wait_until='networkidle', timeout=self.config.timeout_seconds * 1000)
            
            # Wait for specific element if provided
            if wait_for:
                await self.page.wait_for_selector(wait_for, timeout=10000)
            
            # Get page content
            content = await self.page.content()
            return content
            
        except Exception as e:
            self.logger.error(f"Playwright error for {url}: {e}")
            return None
    
    @abstractmethod
    async def crawl(self) -> List[Dict]:
        """
        Crawl vendor site and return list of raw offer data.
        
        Each offer dict should contain:
        - title: str
        - expiry: str or datetime (optional)
        - discount_percent: float (optional)
        - estimated_value: float
        - categories: List[str]
        - terms: str
        - url: str
        - source_type: 'api' or 'scrape'
        """
        pass
    
    async def close(self):
        """Clean up resources."""
        try:
            if self.session:
                await self.session.close()
        except Exception as e:
            self.logger.debug(f"Error closing session: {e}")
        
        try:
            if self.page:
                await self.page.close()
        except Exception as e:
            self.logger.debug(f"Error closing page: {e}")
        
        try:
            if self.browser:
                await self.browser.close()
        except Exception as e:
            self.logger.debug(f"Error closing browser: {e}")
        
        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            self.logger.debug(f"Error stopping playwright: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

