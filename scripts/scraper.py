"""
SHL Product Catalog Scraper
Main scraping script for extracting assessment information
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class SHLCatalogScraper:
    def __init__(self):
        self.base_url = "https://www.shl.com"
        self.catalog_url = "https://www.shl.com/products/product-catalog"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.products = []
        
    def fetch_page(self, url):
        """Fetch a page with error handling"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(1)  # Be respectful to the server
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_product_links(self, soup):
        """Extract all product links from the catalog page"""
        links = []
        
        # Find all product links in the tables
        for link in soup.find_all('a', href=re.compile(r'/products/product-catalog/view/')):
            product_url = urljoin(self.base_url, link['href'])
            product_name = link.text.strip()
            
            if product_name and product_url not in [l['url'] for l in links]:
                links.append({
                    'name': product_name,
                    'url': product_url
                })
                
        logging.info(f"Found {len(links)} product links")
        return links
    
    def extract_product_details(self, url, name):
        """Extract detailed information from a product page"""
        response = self.fetch_page(url)
        if not response:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product = {
            'name': name,
            'url': url,
            'description': '',
            'category': '',
            'test_type': '',
            'duration': '',
            'remote_testing': '',
            'adaptive': '',
            'skills': [],
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract description
        desc_elem = soup.find('div', class_='product-description')
        if desc_elem:
            product['description'] = desc_elem.get_text(strip=True)
        
        # Extract metadata from tables or definition lists
        for dt in soup.find_all('dt'):
            key = dt.get_text(strip=True).lower()
            dd = dt.find_next_sibling('dd')
            if dd:
                value = dd.get_text(strip=True)
                
                if 'test type' in key:
                    product['test_type'] = value
                elif 'duration' in key or 'time' in key:
                    product['duration'] = value
                elif 'remote' in key:
                    product['remote_testing'] = value
                elif 'adaptive' in key:
                    product['adaptive'] = value
                elif 'category' in key:
                    product['category'] = value
        
        # Extract skills/competencies
        skills_section = soup.find('div', class_='skills') or soup.find('ul', class_='competencies')
        if skills_section:
            product['skills'] = [li.get_text(strip=True) for li in skills_section.find_all('li')]
        
        logging.info(f"Scraped: {name}")
        return product
    
    def scrape_catalog(self):
        """Main scraping function"""
        logging.info("Starting catalog scrape...")
        
        # Fetch main catalog page
        response = self.fetch_page(self.catalog_url)
        if not response:
            logging.error("Failed to fetch catalog page")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all product links
        product_links = self.extract_product_links(soup)
        
        # Scrape each product page
        total = len(product_links)
        for idx, link in enumerate(product_links, 1):
            logging.info(f"Processing {idx}/{total}: {link['name']}")
            
            product_data = self.extract_product_details(link['url'], link['name'])
            if product_data:
                self.products.append(product_data)
            
            # Add delay between requests
            time.sleep(2)
        
        logging.info(f"Scraping complete! Total products: {len(self.products)}")
        return self.products
    
    def save_to_json(self, filename='data/raw/shl_catalog_raw.json'):
        """Save scraped data to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        logging.info(f"Data saved to {filename}")
    
    def save_to_csv(self, filename='data/raw/shl_catalog_raw.csv'):
        """Save scraped data to CSV"""
        import pandas as pd
        df = pd.DataFrame(self.products)
        df.to_csv(filename, index=False, encoding='utf-8')
        logging.info(f"Data saved to {filename}")


def main():
    """Main execution function"""
    scraper = SHLCatalogScraper()
    
    # Scrape the catalog
    products = scraper.scrape_catalog()
    
    if products:
        # Save in both formats
        scraper.save_to_json()
        scraper.save_to_csv()
        
        print(f"\n✓ Successfully scraped {len(products)} products")
        print(f"✓ Data saved to 'data/raw/' directory")
    else:
        print("\n✗ No products were scraped")


if __name__ == "__main__":
    main()