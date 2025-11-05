"""
Helper utility functions.
"""
import re
from typing import List
from urllib.parse import urlparse


def generate_product_id(product_name: str) -> str:
    """
    Generate a unique product ID from product name.
    Converts to lowercase, replaces spaces with hyphens, removes special chars.
    """
    # Convert to lowercase
    product_id = product_name.lower()
    # Replace spaces and special chars with hyphens
    product_id = re.sub(r'[^a-z0-9]+', '-', product_id)
    # Remove leading/trailing hyphens
    product_id = product_id.strip('-')
    # Remove multiple consecutive hyphens
    product_id = re.sub(r'-+', '-', product_id)
    return product_id


def extract_domain(url: str) -> str:
    """Extract domain name from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return "unknown"


def extract_platform_name(url: str) -> str:
    """Extract platform name from URL (e.g., amazon, flipkart, etc.)."""
    domain = extract_domain(url).lower()
    # Common platform mappings
    platform_map = {
        'amazon': 'amazon',
        'flipkart': 'flipkart',
        'myntra': 'myntra',
        'snapdeal': 'snapdeal',
        'nykaa': 'nykaa',
        'croma': 'croma',
        'reliance': 'reliance digital',
    }
    
    for key, value in platform_map.items():
        if key in domain:
            return value
    
    return domain.split('.')[0] if domain else "unknown"

