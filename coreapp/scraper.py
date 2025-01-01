from datetime import datetime
import requests
from bs4 import BeautifulSoup
from typing import Tuple, Dict, Optional, List, Any
import pytz
import logging
import requests
import json

logger = logging.getLogger(__name__)
class ScraperError(Exception):
    """Custom exception for scraper errors"""
    pass

def get_specifications(invoice_number: str, token: str, max_retries: int = 3) -> List[Dict]:
    """
    Get bill specifications from the API with retry mechanism
    """
    url = 'https://suf.purs.gov.rs/v/specification'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36',
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://suf.purs.gov.rs/',
        'Origin': 'https://suf.purs.gov.rs'
    }
    
    payload = {
        'invoiceNumber': invoice_number,
        'token': token.strip()  # Remove any whitespace
    }

    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1}: Making specifications request")
            logger.debug(f"Payload: {payload}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            logger.debug(f"Response content: {response.text[:500]}...")  # Log first 500 chars
            
            if response.status_code == 404:
                logger.warning("Specifications not found")
                return []
                
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                specs = data.get('items', [])
                logger.info(f"Successfully retrieved {len(specs)} specifications")
                return specs
            
            # If we didn't get success=True, wait briefly before retry
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            if attempt == max_retries - 1:
                raise ScraperError(f"Failed to get specifications after {max_retries} attempts") from e
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ScraperError("Invalid JSON response from server") from e

def scrape_bill_and_specs(url: str) -> Tuple[Dict, List[Dict]]:
    """
    Scrape both bill info and specifications with enhanced error handling
    """
    logger.debug(f"Starting to scrape URL: {url}")
    
    try:
        # First get the bill info
        bill_data = scrape_bill_info(url)
        logger.debug(f"Got bill data: {bill_data}")
        
        # Extract invoice number - handle different possible formats
        invoice_number = bill_data.get('cnt')
        if not invoice_number:
            raise ScraperError("Could not find invoice number in bill data")
            
        # Extract and clean token
        try:
            token = url.split('vl=')[1]
            # Remove any URL fragments
            token = token.split('#')[0]
            # URL decode
            token = requests.utils.unquote(token)
        except IndexError:
            raise ScraperError("Could not extract token from URL")
            
        logger.debug(f"Using invoice_number: {invoice_number}, token: {token}")
        
        # Get specifications with retry mechanism
        specs = get_specifications(invoice_number, token)
        
        # Transform specification data
        processed_specs = []
        for spec in specs:
            try:
                processed_spec = {
                    'gtin': spec.get('gtin', ''),
                    'name': spec.get('name', ''),
                    'quantity': float(spec.get('quantity', 0)),
                    'unit_price': float(spec.get('unitPrice', 0)),
                    'total': float(spec.get('total', 0)),
                    'tax_base_amnt': float(spec.get('taxBaseAmount', 0)),
                    'vat': float(spec.get('vatAmount', 0)),
                    'label': spec.get('label', ''),
                    'label_rate': float(spec.get('labelRate', 0))
                }
                processed_specs.append(processed_spec)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error processing specification item: {str(e)}")
                continue
                
        logger.info(f"Successfully processed {len(processed_specs)} specifications")
        return bill_data, processed_specs
        
    except Exception as e:
        logger.error(f"Error in scrape_bill_and_specs: {str(e)}")
        raise ScraperError(f"Failed to scrape bill and specifications: {str(e)}") from e

def scrape_bill_info(url: str) -> Dict[str, Optional[str]]:
    """Scrapes bill information from the provided URL."""
    logger.debug(f"Starting to scrape bill info from URL: {url}")
    
    try:
        # Get the page content
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Helper function to safely extract text from span elements
        def get_span_text(span_id: str) -> Optional[str]:
            span = soup.find('span', id=span_id)
            value = span.text.strip() if span else None
            logger.debug(f"Found span {span_id}: {value}")
            return value
            
        # Helper function to get text after label
        def get_label_value(label_text: str) -> Optional[str]:
            label = soup.find('label', class_='col-form-label', string=lambda x: x and label_text in x)
            if label:
                div = label.find_next('div', class_='col-md-12')
                if div:
                    value = ' '.join(div.text.strip().split())
                    logger.debug(f"Found label {label_text}: {value}")
                    return value
            logger.debug(f"No value found for label {label_text}")
            return None

        # Get raw values
        raw_total = get_label_value('Укупан износ')
        raw_server_time = get_label_value('ПФР време')
        
        # Extract and log all fields
        bill_data = {
            'pib': get_span_text('tinLabel'),
            'store': get_span_text('shopFullNameLabel'),
            'address': get_label_value('Адреса'),
            'city': get_label_value('Град'),
            'municipality': get_label_value('Општина'),
            'buyer_id': get_label_value('ИД купца'),
            'asked': get_label_value('Затражио'),
            'type': get_label_value('Врста'),
            'total': convert_decimal(raw_total) if raw_total else None,
            'cnt_type': get_label_value('Бројач по врсти трансакције'),
            'cnt_total': get_label_value('Бројач укупног броја'),
            'ext': get_label_value('Екстензија бројача рачуна'),
            'cnt': get_label_value('Затражио - Потписао - Бројач'),
            'signed': get_label_value('Потписао'),
            'server_time': convert_date(raw_server_time) if raw_server_time else None
        }
        
        logger.debug("Extracted bill data:")
        for key, value in bill_data.items():
            logger.debug(f"{key}: '{value}'")
            
        return bill_data

    except requests.RequestException as e:
        logger.error(f"Error fetching the URL: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error parsing the page: {str(e)}")
        raise

# def scrape_bill_info(url: str) -> Dict[str, Optional[str]]:
#     """
#     Scrapes bill information from the provided URL.
#     Returns a dictionary with bill details or None for empty fields.
#     """
#     try:
#         # Get the page content
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for bad status codes
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Helper function to safely extract text from span elements
#         def get_span_text(span_id: str) -> Optional[str]:
#             span = soup.find('span', id=span_id)
#             return span.text.strip() if span else None
            
#         # Helper function to get text after label
#         def get_label_value(label_text: str) -> Optional[str]:
#             label = soup.find('label', class_='col-form-label', string=lambda x: x and label_text in x)
#             if label:
#                 div = label.find_next('div', class_='col-md-12')
#                 if div:
#                     return div.text.strip()
#             return None
        

#         raw_total = get_label_value('Укупан износ')
#         raw_server_time = get_label_value('ПФР време')
        

#         # Extract all required fields
#         bill_data = {
#             'pib': get_span_text('tinLabel'),
#             'store': get_span_text('shopFullNameLabel'),
#             'address': get_label_value('Адреса'),
#             'city': get_label_value('Град'),
#             'municipality': get_label_value('Општина'),
#             'buyer_id': get_label_value('ИД купца'),
#             'asked': get_label_value('Затражио'),
#             'type': get_label_value('Врста'),
#             'total': convert_decimal(raw_total) if raw_total else None,
#             'cnt_type': get_label_value('Бројач по врсти трансакције'),
#             'cnt_total': get_label_value('Бројач укупног броја'),
#             'ext': get_label_value('Екстензија бројача рачуна'),
#             'cnt': get_label_value('Затражио - Потписао - Бројач'),
#             'signed': get_label_value('Потписао'),
#             'server_time': convert_date(raw_server_time) if raw_server_time else None,
#         }

#         # print("All raw values:")
#         # for key, value in bill_data.items():
#         #     print(f"{key}: '{value}'")

#         return bill_data
    
#     except Exception as e:
#         print(f"Error in scrape_bill_info: {str(e)}")
#         raise e
#     except requests.RequestException as e:
#         raise Exception(f"Error fetching the URL: {str(e)}")
#     except Exception as e:
#         raise Exception(f"Error parsing the page: {str(e)}")


# # def fetch_bill_specs(api_url: str, headers: dict = None, payload: dict = None) -> list:
#     """Fetch bill specifications from the API."""
#     response = requests.post(api_url, headers=headers, json=payload)
#     print(response.status_code)
#     print(response.text)
#     try:
#         response.raise_for_status()
#         data = response.json()
#         if data.get("success"):
#             return data.get("items", [])
#         else:
#             print(f"API Response: {data}")  # Debugging
#             raise ValueError("API response indicates failure.")
#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")  # Debugging
#         raise ConnectionError(f"Failed to fetch data: {e}")


# def scrape_bill_specs(api_url: str) -> list:
    """Fetch and process bill specifications from the API."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36'
        # Add session cookies or authentication tokens here if needed
    }
    try:

        api_url = "https://suf.purs.gov.rs/specifications"
        items = fetch_bill_specs(api_url, headers=headers)
        # Process items if needed (convert decimals, clean strings, etc.)
        specs = [
            {
                "gtin": item["gtin"],
                "name": item["name"],
                "quantity": item["quantity"],
                "unit_price": item["unitPrice"],
                "total": item["total"],
                "label": item["label"],
                "label_rate": item["labelRate"],
                "tax_base_amount": item["taxBaseAmount"],
                "vat_amount": item["vatAmount"],
            }
            for item in items
        ]

        print("All raw values:")
        for key, value in specs.items():
            print(f"{key}: '{value}'")    

        return specs
    except Exception as e:
        print(f"Error fetching specifications: {e}")
        return []


# def scrape_bill_specs(soup) -> List[Dict[str, Any]]:
#     """Scrapes the bill specifications table"""
#     specs = []
#     # Find the specifications table
#     table = soup.find('table', class_='invoice-table')
#     if table:
#         # Get all specification rows (skipping header)
#         rows = table.find_all('tr')[1:]  # Skip header row
#         for row in rows:
#             # Get all cells in the row
#             cells = row.find_all('td')
#             if len(cells) >= 7:  # Ensure we have all needed cells
#                 spec = {
#                     'name': cells[0].find('strong').text.strip(),
#                     'quantity': convert_decimal(cells[1].text.strip()),
#                     'unit_price': convert_decimal(cells[2].text.strip()),
#                     'total': convert_decimal(cells[3].text.strip()),
#                     'tax_base_amnt': convert_decimal(cells[4].text.strip()),
#                     'vat': convert_decimal(cells[5].text.strip()),
#                     'label': cells[6].text.strip()
#                 }
#                 specs.append(spec)
#     return specs
    
def convert_decimal(value: str) -> float:
    """Convert Serbian decimal format to Python decimal"""
    if not value or value.strip() == '':
        return None
    try:
        return float(value.replace('.', '').replace(',', '.'))
    except ValueError as e:
        print(f"Failed to convert value: '{value}'")  # This will help us identify the problematic field
        raise e

def convert_date(date_str: str) -> str:
    """Convert Serbian date format to a timezone-aware Django datetime"""
    if not date_str:
        return None
    try:
        # Convert "9.11.2024. 17:03:36" to a naive datetime
        naive_dt = datetime.strptime(date_str.strip(), '%d.%m.%Y. %H:%M:%S')
        # Convert naive datetime to an aware datetime
        aware_dt = pytz.timezone('Europe/Belgrade').localize(naive_dt)
        return aware_dt
    except ValueError:
        return None
    
def get_label_value(label_text: str) -> Optional[str]:
    label = soup.find('label', class_='col-form-label', string=lambda x: x and label_text in x)
    if label:
        div = label.find_next('div', class_='col-md-12')
        if div:
            # Clean the text by replacing newlines with spaces and stripping extra whitespace
            return ' '.join(div.text.strip().split())
    return None