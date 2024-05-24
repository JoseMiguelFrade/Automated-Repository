import logging
from functools import lru_cache
from .proxy import ProxyManager
import re
from urllib.parse import urlparse,urlunparse
import hashlib

pm = ProxyManager()
log = logging.getLogger(__name__)

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https']

def clean_url(url):

    parsed = urlparse(url)

    # add scheme if not available
    if not parsed.scheme:
        parsed = parsed._replace(scheme="http")

        url = urlunparse(parsed)

    # Check if URL is valid
    if not is_valid_url(url):
        # Handle invalid URL (e.g., skip, log an error, etc.)
        return None
    # clean text anchor from urls if available
    pattern = r'(.+)(\/#[a-zA-Z0-9]+)$'
    m = re.match(pattern, url)

    if m:
        return m.group(1)
    else:
        # clean trailing slash if available
        pattern = r'(.+)(\/)$'
        m = re.match(pattern, url)

        if m:
            return m.group(1)

    return url

def normalize_url(url):
    parsed_url = urlparse(url)
    # Create a new URL without the query and fragment
    normalized_url = urlunparse(parsed_url._replace(query="", fragment=""))
    return normalized_url



def get_content_type(response):
    content_type = response.headers.get("content-type")
    print(f"content type na func: {content_type}")
    if content_type:
        return content_type.split(';')[0].strip()


@lru_cache(maxsize=8192)
def call(session, url, use_proxy=False, retries=0):
    if use_proxy:
        proxy = pm.get_proxy()
        if proxy[0]:
            try:
                response = session.get(url, timeout=20, proxies=proxy[0], verify=False)
                response.raise_for_status()
            except Exception as e:
                if retries <= 3:
                    pm.change_proxy(proxy[1])
                    return call(session, url, True, retries + 1)
                else:
                    return None
            else:
                return response
        else:
            return None
    else:
        try:
            response = session.get(url, timeout=20, verify=False)
            response.raise_for_status()
        except Exception as e:
            # try with proxy
            return call(session,url,use_proxy=True)
        else:
            return response

def parse_result_to_dict(result_str):
    # Split the result string by '#'
    elements = result_str.split('#')
    result_dict = {}

    # Iterate over each element and further split by ':'
    for element in elements:
        key_value = element.split(':', 1)  # Split only on the first ':' to handle multiple ':' in value
        if len(key_value) == 2:
            key, value = key_value
            key = key.strip().lower().replace(" ", "_")
            #remove < > from value
            value = value.replace("<","").replace(">","")
            # Map the key from the response to the dictionary fields
            if key == "is_related":
                result_dict["is_related"] = value.strip()
            if key == "title":
                result_dict["title"] = value.strip()
            elif key == "issuer":
                result_dict["issuer"] = value.strip()
            elif key == "origin":
                result_dict["origin"] = value.strip()
            elif key == "date":
                result_dict["date"] = value.strip()
            elif key == "type":
                result_dict["type"] = value.strip()
            elif key == "subject":
                result_dict["subject"] = value.strip()
            elif key == "area":
                result_dict["area"] = value.strip()
            elif key == "related_docs":
                # Assuming the related documents are separated by |
                docs = value.strip().split('|')
                result_dict["related_docs"] = [doc.replace('|', '') for doc in docs]
            elif key == "abstract":
                result_dict["abstract"] = value.strip()
            # Add additional mappings as needed

    
   

    return result_dict

def compute_md5(file_data):
    """Compute MD5 hash for the given file data."""
    hash_md5 = hashlib.md5()
    hash_md5.update(file_data)
    return hash_md5.hexdigest()

def format_date(date):
    """Format date to 'hh:mm:ss dd/mm/yyyy'."""
    return date.strftime('%H:%M:%S %d/%m/%Y')