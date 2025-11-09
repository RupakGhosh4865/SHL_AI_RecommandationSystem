"""
Test scraper on a few products
"""
import requests
from bs4 import BeautifulSoup
import json

def test_single_product():
    url = "https://www.shl.com/products/product-catalog/view/administrative-professional-short-form/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("✓ Successfully fetched page")
    print(f"Title: {soup.title.string if soup.title else 'No title'}")
    
    # Print first 500 characters
    print("\nPage content preview:")
    print(soup.get_text()[:500])

if __name__ == "__main__":
    test_single_product()