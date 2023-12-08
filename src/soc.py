"""Core functions for interacting with Rutgers Schedule of Classes (SOC)"""
from urllib.parse import urlencode, quote
import requests
import logging
from typing import List
import config

REGISTER_BUTTON_IMAGE = "src/register_button.png"
LOGIN_BUTTON_IMAGE = "src/login_button.png"
SEMESTER = config.QUERY_PARAMS_WEBREG["semesterSelection"]

# turn off logging for urllib3
logging.getLogger("urllib3").setLevel(logging.ERROR)

def construct_api_url(query_params: dict) -> str:
    """
    Construct the API URL for Rutgers SOC using query parameters.
    
    Args:
        query_params: Dictionary of query parameters for the API.
        
    Returns:
        Constructed API URL as a string.
    """
    params_encoded = urlencode(query_params, quote_via=quote)
    api_url = f"http://sis.rutgers.edu/soc/api/openSections.gzip?{params_encoded}"
    return api_url

def fetch_open_sections(api_url: str, retry_limit: int = 5) -> List[str]:
    """
    Fetch all open section index numbers from SOC.

    Args:
        api_url: The SOC API endpoint to hit.
        retry_limit: The maximum number of retries for API requests.

    Returns:
        A list of open section index numbers, or raises an exception after retries exceed the limit.
    """
    for attempt in range(retry_limit):
        try:
            response = requests.get(api_url, timeout=0.3)
            response.raise_for_status()
            return response.json()
        except:
            pass

    raise Exception("Max retries reached while fetching open sections.")

def is_section_open(section: str, open_sections: List[str]) -> bool:
    """
    Check if a section is open by performing a binary search on the sorted list of open sections.
    
    Args:
        section: The section index number to check.
        open_sections: A sorted list of open section index numbers.
    
    Returns:
        True if the section is open, otherwise False.
    """
    left, right = 0, len(open_sections) - 1
    while left <= right:
        mid = (left + right) // 2
        if open_sections[mid] == section:
            return True
        elif open_sections[mid] < section:
            left = mid + 1
        else:
            right = mid - 1
    return False