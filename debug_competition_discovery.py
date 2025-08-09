#!/usr/bin/env python3
"""
Debug script to identify why competition discovery is hanging.
"""
import sys
import os
import logging
import requests
from bs4 import BeautifulSoup
import time

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

# Setup basic logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_basic_request():
    """Test basic HTTP request to FBRef competitions page."""
    url = "https://fbref.com/en/comps/"
    
    logger.info(f"Testing basic request to: {url}")
    
    try:
        # Create session with timeout
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        logger.info("Making HTTP request...")
        start_time = time.time()
        
        # Short timeout to avoid hanging
        response = session.get(url, timeout=(5, 10))
        
        end_time = time.time()
        logger.info(f"Request completed in {end_time - start_time:.2f} seconds")
        
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response size: {len(response.text)} bytes")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Check for competition tables
            tables = soup.select("table.stats_table")
            logger.info(f"Found {len(tables)} competition tables")
            
            if tables:
                # Check first table structure
                first_table = tables[0]
                tbody = first_table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    logger.info(f"First table has {len(rows)} rows")
                    
                    # Check first few rows
                    for i, row in enumerate(rows[:3]):
                        th_cell = row.find('th', {'data-stat': 'league_name'})
                        gender_cell = row.find('td', {'data-stat': 'gender'})
                        
                        if th_cell and th_cell.find('a'):
                            link = th_cell.find('a')
                            name = link.text.strip()
                            url_comp = link.get('href')
                            gender = gender_cell.text.strip() if gender_cell else "N/A"
                            
                            logger.info(f"Row {i+1}: {name} | Gender: {gender} | URL: {url_comp}")
                
                return True
            else:
                logger.error("No competition tables found!")
                # Save HTML for debugging
                with open('debug_competitions_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.info("HTML saved to debug_competitions_page.html")
                return False
        else:
            logger.error(f"HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout: {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def test_fbref_utils():
    """Test the fbref_utils fazer_requisicao function."""
    try:
        from Coleta_de_dados.apis.fbref.fbref_utils import fazer_requisicao, BASE_URL
        
        url = f"{BASE_URL}/en/comps/"
        logger.info(f"Testing fbref_utils.fazer_requisicao with: {url}")
        
        start_time = time.time()
        soup = fazer_requisicao(url)
        end_time = time.time()
        
        logger.info(f"fbref_utils request completed in {end_time - start_time:.2f} seconds")
        
        if soup:
            tables = soup.select("table.stats_table")
            logger.info(f"Found {len(tables)} tables using fbref_utils")
            return True
        else:
            logger.error("fbref_utils returned None")
            return False
            
    except Exception as e:
        logger.error(f"Error testing fbref_utils: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Starting Competition Discovery Debug ===")
    
    # Test 1: Basic HTTP request
    logger.info("\n--- Test 1: Basic HTTP Request ---")
    basic_success = test_basic_request()
    
    # Test 2: fbref_utils function
    logger.info("\n--- Test 2: FBRef Utils Function ---")
    utils_success = test_fbref_utils()
    
    # Summary
    logger.info(f"\n=== Debug Summary ===")
    logger.info(f"Basic HTTP request: {'SUCCESS' if basic_success else 'FAILED'}")
    logger.info(f"FBRef utils function: {'SUCCESS' if utils_success else 'FAILED'}")
    
    if not basic_success:
        logger.error("Basic HTTP request failed - network or site access issue")
    elif not utils_success:
        logger.error("FBRef utils failed - issue with utility functions")
    else:
        logger.info("Both tests passed - issue might be in the main logic")
