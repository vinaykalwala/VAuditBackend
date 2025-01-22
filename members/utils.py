import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def fetch_keywords_from_url(url: str) -> List[str]:
    """Extract keywords from a given URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract meta keywords or any other way to determine keywords
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keywords:
        keywords = meta_keywords.get('content', '').split(',')
        return [keyword.strip() for keyword in keywords]
    return []

def find_content_gaps(your_url: str, competitor_urls: List[str]) -> Dict:
    your_keywords = set(fetch_keywords_from_url(your_url))
    gaps = []

    for competitor_url in competitor_urls:
        competitor_keywords = set(fetch_keywords_from_url(competitor_url))
        missing_keywords = competitor_keywords - your_keywords
        if missing_keywords:
            gaps.append({
                'competitor_url': competitor_url,
                'missing_keywords': list(missing_keywords)
            })
    
    return {'your_url': your_url, 'gaps': gaps}


# import requests
# from typing import List, Dict

# def fetch_backlinks(url: str) -> List[str]:
#     """Fetch backlinks for a given URL. Here we assume using an external API or scraping."""
#     # Placeholder function - replace with actual API calls or scraping logic
#     response = requests.get(f"https://api.example.com/backlinks?url={url}")
#     backlinks = response.json().get('backlinks', [])
#     return backlinks

# def monitor_backlinks(url: str, previous_backlinks: List[str]) -> Dict:
#     """Detect new and lost backlinks compared to the previous list."""
#     current_backlinks = fetch_backlinks(url)
#     new_backlinks = set(current_backlinks) - set(previous_backlinks)
#     lost_backlinks = set(previous_backlinks) - set(current_backlinks)

#     return {
#         'new_backlinks': list(new_backlinks),
#         'lost_backlinks': list(lost_backlinks)
#     }










# analysis/utils.py
import requests
from bs4 import BeautifulSoup
import re
import time

def fetch_page_content(url):
    """Fetch the content of the given URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

def extract_keywords(content):
    """Extract keywords from the page content. This is a basic implementation."""
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    words = text.split()
    keywords = [word for word in words if len(word) > 4]  # Simple keyword extraction
    return keywords

def extract_backlinks(content):
    """Extract backlinks from the page content."""
    soup = BeautifulSoup(content, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href']]
    return links

def extract_internal_external_links(content, base_url):
    """Extract internal and external links from the page content."""
    soup = BeautifulSoup(content, 'html.parser')
    internal_links = []
    external_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if base_url in href:
            internal_links.append(href)
        elif href.startswith('http'):
            external_links.append(href)
    return internal_links, external_links

def extract_meta_description(content):
    """Extract meta description from the page content."""
    soup = BeautifulSoup(content, 'html.parser')
    meta_description = soup.find('meta', attrs={'name': 'description'})
    return meta_description['content'] if meta_description else ''

def extract_headings(content):
    """Extract headings (h1, h2, h3) from the page content."""
    soup = BeautifulSoup(content, 'html.parser')
    headings = {
        'h1': [h.get_text() for h in soup.find_all('h1')],
        'h2': [h.get_text() for h in soup.find_all('h2')],
        'h3': [h.get_text() for h in soup.find_all('h3')],
    }
    return headings

def extract_image_alt_text(content):
    """Extract alt text from images in the page content."""
    soup = BeautifulSoup(content, 'html.parser')
    alt_texts = [img['alt'] for img in soup.find_all('img', alt=True)]
    return alt_texts

def calculate_keyword_density(content, keywords):
    """Calculate keyword density."""
    word_count = len(content.split())
    keyword_count = sum(content.lower().count(keyword.lower()) for keyword in keywords)
    return (keyword_count / word_count) * 100 if word_count > 0 else 0

def calculate_readability(content):
    """Calculate basic readability scores."""
    words = content.split()
    sentences = re.split(r'[.!?]', content)
    syllables = sum([len(re.findall(r'[aeiouy]+', word)) for word in words])
    word_count = len(words)
    sentence_count = len(sentences)
    score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllables / word_count)
    return {
        'flesch_kincaid': score
    }

def calculate_page_load_time(url):
    """Calculate the page load time."""
    start_time = time.time()
    requests.get(url)
    load_time = time.time() - start_time
    return load_time

def analyze_urlinfo(url):
    """Analyze the given URL for SEO data."""
    content = fetch_page_content(url)
    if content:
        keywords = extract_keywords(content)
        backlinks = extract_backlinks(content)
        meta_description = extract_meta_description(content)
        headings = extract_headings(content)
        alt_texts = extract_image_alt_text(content)
        internal_links, external_links = extract_internal_external_links(content, url)
        keyword_density = calculate_keyword_density(content, keywords)
        readability_scores = calculate_readability(content)
        page_load_time = calculate_page_load_time(url)

        return {
            'keywords': keywords,
            'backlinks': backlinks,
            'meta_description': meta_description,
            'headings': headings,
            'alt_texts': alt_texts,
            'internal_links': internal_links,
            'external_links': external_links,
            'keyword_density': keyword_density,
            'readability_scores': readability_scores,
            'page_load_time': page_load_time,
            'content': content
        }
    return None

def compare_seo_data(user_data, competitor_data):
    """Compare SEO data between user and competitor."""
    comparison = {
        'keyword_overlap': list(set(user_data['keywords']) & set(competitor_data['keywords'])),
        'backlink_comparison': {
            'user_backlinks': user_data['backlinks'],
            'competitor_backlinks': competitor_data['backlinks'],
        },
        'content_comparison': {
            'user_content_length': len(user_data['content']),
            'competitor_content_length': len(competitor_data['content']),
        },
        'meta_description_comparison': {
            'user_meta_description': user_data['meta_description'],
            'competitor_meta_description': competitor_data['meta_description'],
        },
        'headings_comparison': {
            'user_headings': user_data['headings'],
            'competitor_headings': competitor_data['headings'],
        },
        'image_alt_text_comparison': {
            'user_alt_texts': user_data['alt_texts'],
            'competitor_alt_texts': competitor_data['alt_texts'],
        },
        'internal_external_links_comparison': {
            'user_internal_links': len(user_data['internal_links']),
            'user_external_links': len(user_data['external_links']),
            'competitor_internal_links': len(competitor_data['internal_links']),
            'competitor_external_links': len(competitor_data['external_links']),
        },
        'keyword_density_comparison': {
            'user_keyword_density': user_data['keyword_density'],
            'competitor_keyword_density': competitor_data['keyword_density'],
        },
        'readability_comparison': {
            'user_readability_scores': user_data['readability_scores'],
            'competitor_readability_scores': competitor_data['readability_scores'],
        },
        'page_load_time_comparison': {
            'user_page_load_time': user_data['page_load_time'],
            'competitor_page_load_time': competitor_data['page_load_time'],
        }
    }
    return comparison

import requests
import base64
import logging

logger = logging.getLogger(__name__)

def get_moz_metrics(url, access_id, secret_key):
    endpoint = "https://lsapi.seomoz.com/v2/url_metrics"
    
    # Encode the access ID and secret key
    auth = base64.b64encode(f"{access_id}:{secret_key}".encode('utf-8')).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "targets": [url],
        "metrics": [
            "pageAuthority", "domainAuthority", "inboundLinks", "linkingRootDomains", 
            "totalLinks", "spamScore", "topPages", "anchorText", "httpStatusCodes", 
            "linkEquity", "canonicalUrl", "mozRank", "mozTrust"
        ]
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()  # Raises HTTPError if the HTTP request returned an unsuccessful status code
        
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Content: {response.content}")

        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None
    
