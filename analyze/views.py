import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse, urljoin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import logging

from analyze.serializers import CrawlingResultSerializer

logger = logging.getLogger(__name__)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt

def overview(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            base_url = response.url

            # Perform various analyses
            internal_urls, internal_statuses = extract_internal_urls(soup, base_url)
            external_urls, external_statuses = extract_external_urls(soup, base_url)
            backlinks, backlinks_statuses = extract_backlinks(soup, base_url, external_urls)
            dofollow_links, dofollow_statuses = extract_links(soup, base_url, 'follow')
            nofollow_links, nofollow_statuses = extract_links(soup, base_url, 'nofollow')
            canonical_urls, canonical_statuses = extract_canonical_urls(soup)
            non_canonical_urls, non_canonical_statuses = extract_non_canonical_urls(soup, base_url)
            crawled_links = internal_urls | external_urls
            uncrawled_links, uncrawled_statuses = find_uncrawled_links(crawled_links, base_url)
            image_count, image_urls, image_statuses = extract_images(soup, base_url)
            broken_images, broken_images_statuses = check_broken_images(image_urls)
            title_info, title_statuses = analyze_titles(soup)
            h1_info, h1_statuses = analyze_h1_tags(soup)
            meta_description_info, meta_description_statuses = analyze_meta_description(soup)
            broken_links, broken_links_statuses = check_broken_links(soup, base_url)
            word_count_info, word_count_statuses = analyze_word_count(soup)
            non_html_files, non_html_files_statuses = find_non_html_files(soup, base_url)
            html_pages, html_pages_statuses = find_html_pages(soup, base_url)

            # Indexed and Non-Indexed URLs
            indexed_urls, indexed_statuses = extract_indexed_urls(html_pages, base_url)
            non_indexed_urls, non_indexed_statuses = extract_non_indexed_urls(html_pages, base_url)

            # Aggregate counts and statuses
            aggregate_counts = {
                'total_crawled_links': len(crawled_links),
                'total_uncrawled_links': len(uncrawled_links),
                'total_indexed_urls': len(indexed_urls),
                'total_non_indexed_urls': len(non_indexed_urls),
                'total_broken_links': len(broken_links),
                'total_image_count': image_count,
                'total_non_html_files': len(non_html_files),
                'total_html_pages': len(html_pages),
                'total_internal_links': len(internal_urls),
                'total_external_links': len(external_urls),
                'total_backlinks': len(backlinks),
                'total_dofollow_links': len(dofollow_links),
                'total_nofollow_links': len(nofollow_links),
                'total_canonical_urls': len(canonical_urls),
                'total_non_canonical_urls': len(non_canonical_urls)
            }

            # Compile results
            results = {
                'internal_urls': {
                    'count': len(internal_urls),
                    'list': list(internal_urls),
                    'status': internal_statuses
                },
                'external_urls': {
                    'count': len(external_urls),
                    'list': list(external_urls),
                    'status': external_statuses
                },
                'backlinks': {
                    'count': len(backlinks),
                    'list': list(backlinks),
                    'status': backlinks_statuses
                },
                'dofollow_links': {
                    'count': len(dofollow_links),
                    'list': list(dofollow_links),
                    'status': dofollow_statuses
                },
                'nofollow_links': {
                    'count': len(nofollow_links),
                    'list': list(nofollow_links),
                    'status': nofollow_statuses
                },
                'canonical_urls': {
                    'count': len(canonical_urls),
                    'list': list(canonical_urls),
                    'status': canonical_statuses
                },
                'non_canonical_urls': {
                    'count': len(non_canonical_urls),
                    'list': list(non_canonical_urls),
                    'status': non_canonical_statuses
                },
                'crawled_links': {
                    'count': len(crawled_links),
                    'list': list(crawled_links)
                },
                'uncrawled_links': {
                    'count': len(uncrawled_links),
                    'list': list(uncrawled_links),
                    'status': uncrawled_statuses
                },
                'image_count': image_count,
                'image_urls': {
                    'count': len(image_urls),
                    'list': list(image_urls),
                    'status': image_statuses
                },
                'broken_images_count': len(broken_images),
                'broken_images': {
                    'count': len(broken_images),
                    'list': list(broken_images),
                    'status': broken_images_statuses
                },
                'title_info': {
                    'data': title_info,
                    'status': title_statuses
                },
                'h1_info': {
                    'data': h1_info,
                    'status': h1_statuses
                },
                'meta_description_info': {
                    'data': meta_description_info,
                    'status': meta_description_statuses
                },
                'broken_links': {
                    'count': len(broken_links),
                    'list': list(broken_links),
                    'status': broken_links_statuses
                },
                'word_count_info': {
                    'data': word_count_info,
                    'status': word_count_statuses
                },
                'non_html_files': {
                    'count': len(non_html_files),
                    'list': list(non_html_files),
                    'status': non_html_files_statuses
                },
                'html_pages': {
                    'count': len(html_pages),
                    'list': list(html_pages),
                    'status': html_pages_statuses
                },
                'indexed_urls': {
                    'count': len(indexed_urls),
                    'list': list(indexed_urls),
                    'status': indexed_statuses
                },
                'non_indexed_urls': {
                    'count': len(non_indexed_urls),
                    'list': list(non_indexed_urls),
                    'status': non_indexed_statuses
                }
            }

            return JsonResponse({
                'aggregate_counts': aggregate_counts,
                'results': results
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def extract_internal_urls(soup, base_url):
    internal_urls = set()
    status = {}
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            internal_urls.add(full_url)
            status[full_url] = get_status_code(full_url)
        else:
            status[full_url] = {'code': 'External', 'status': 'External'}
    return internal_urls, status

def extract_external_urls(soup, base_url):
    external_urls = set()
    status = {}
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc != urlparse(base_url).netloc:
            external_urls.add(full_url)
            status[full_url] = get_status_code(full_url)
        else:
            status[full_url] = {'code': 'Internal', 'status': 'Internal'}
    return external_urls, status

def extract_backlinks(soup, base_url, external_urls):
    backlinks = set()
    status = {}
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if full_url in external_urls:
            backlinks.add(full_url)
            status[full_url] = get_status_code(full_url)
        else:
            status[full_url] = {'code': 'Not a backlink', 'status': 'Not a backlink'}
    return backlinks, status

def extract_links(soup, base_url, rel_type):
    links = set()
    status = {}
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        rel = link.get('rel', [])
        if rel_type == 'follow' and 'nofollow' not in rel:
            links.add(full_url)
            status[full_url] = get_status_code(full_url)
        elif rel_type == 'nofollow' and 'nofollow' in rel:
            links.add(full_url)
            status[full_url] = get_status_code(full_url)
        else:
            status[full_url] = {'code': 'Irrelevant', 'status': 'Irrelevant'}
    return links, status

def extract_canonical_urls(soup):
    canonical_urls = set()
    status = {}
    canonical_link = soup.find('link', rel='canonical')
    if canonical_link:
        href = canonical_link.get('href')
        full_url = urljoin(soup.base_url, href)
        canonical_urls.add(full_url)
        status[full_url] = get_status_code(full_url) + ' - Canonical'
    else:
        status['None'] = 'No Canonical Link Found'
    return canonical_urls, status

def extract_non_canonical_urls(soup, base_url):
    non_canonical_urls = set()
    status = {}
    canonical_urls = extract_canonical_urls(soup)[0]
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if full_url not in canonical_urls:
            non_canonical_urls.add(full_url)
            status[full_url] = get_status_code(full_url) + ' - Non-Canonical'
        else:
            status[full_url] = get_status_code(full_url) + ' - Canonical'
    return non_canonical_urls, status

def find_uncrawled_links(crawled_links, base_url):
    uncrawled_links = set()
    status = {}
    all_links = extract_internal_urls(BeautifulSoup(requests.get(base_url).content, 'html.parser'), base_url)[0]
    for link in all_links:
        if link not in crawled_links:
            uncrawled_links.add(link)
            status[link] = get_status_code(link) + ' - Uncrawled'
    return uncrawled_links, status

def extract_images(soup, base_url):
    image_urls = set()
    status = {}
    image_count = 0
    for img in soup.find_all('img', src=True):
        src = img['src']
        full_url = urljoin(base_url, src)
        image_urls.add(full_url)
        status[full_url] = get_status_code(full_url) + ' - Image Found'
        image_count += 1
    return image_count, image_urls, status

def check_broken_images(image_urls):
    broken_images = set()
    status = {}
    for url in image_urls:
        try:
            response = requests.head(url, allow_redirects=True)
            if response.status_code != 200:
                broken_images.add(url)
                status[url] = get_status_code(url) + ' - Broken'
            else:
                status[url] = get_status_code(url) + ' - Working'
        except requests.RequestException:
            broken_images.add(url)
            status[url] = get_status_code(url) + ' - Broken'
    return broken_images, status

def analyze_titles(soup):
    title_info = []
    status = []
    title_tag = soup.find('title')
    if title_tag:
        title_info.append(title_tag.text)
        status.append('Present')
    else:
        title_info.append('')
        status.append('Missing')
    return title_info, status

def analyze_h1_tags(soup):
    h1_info = []
    status = []
    for h1 in soup.find_all('h1'):
        h1_info.append(h1.text)
        status.append('Present')
    if not h1_info:
        status.append('Missing')
    return h1_info, status

def analyze_meta_description(soup):
    meta_description_info = []
    status = []
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        meta_description_info.append(meta_description.get('content', ''))
        status.append('Present')
    else:
        meta_description_info.append('')
        status.append('Missing')
    return meta_description_info, status

def check_broken_links(soup, base_url):
    broken_links = set()
    status = {}
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        try:
            response = requests.head(full_url, allow_redirects=True)
            if response.status_code >= 400:
                broken_links.add(full_url)
                status[full_url] = get_status_code(full_url) + ' - Broken'
            else:
                status[full_url] = get_status_code(full_url) + ' - Working'
        except requests.RequestException:
            broken_links.add(full_url)
            status[full_url] = get_status_code(full_url) + ' - Broken'
    return broken_links, status

def analyze_word_count(soup):
    word_count_info = []
    status = []
    for p in soup.find_all('p'):
        word_count = len(p.text.split())
        word_count_info.append(word_count)
        status.append('OK')
    return word_count_info, status

def find_non_html_files(soup, base_url):
    non_html_files = set()
    status = {}
    for link in soup.find_all('a', href=True):
        href = link['href']
        if not href.endswith('.html'):
            full_url = urljoin(base_url, href)
            non_html_files.add(full_url)
            status[full_url] = get_status_code(full_url) + ' - Non-HTML File'
    return non_html_files, status

def find_html_pages(soup, base_url):
    html_pages = set()
    status = {}
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.html'):
            full_url = urljoin(base_url, href)
            html_pages.add(full_url)
            status[full_url] = get_status_code(full_url) + ' - HTML Page'
    return html_pages, status

def extract_indexed_urls(html_pages, base_url):
    indexed_urls = set()
    status = {}
    for url in html_pages:
        try:
            response = requests.get(url)
            if 'X-Robots-Tag: noindex' not in response.headers.get('X-Robots-Tag', ''):
                indexed_urls.add(url)
                status[url] = get_status_code(url) + ' - Indexed'
            else:
                status[url] = get_status_code(url) + ' - Non-Indexed'
        except requests.RequestException:
            status[url] = get_status_code(url) + ' - Error'
    return indexed_urls, status

def extract_non_indexed_urls(html_pages, base_url):
    non_indexed_urls = set()
    status = {}
    for url in html_pages:
        try:
            response = requests.get(url)
            if 'X-Robots-Tag: noindex' in response.headers.get('X-Robots-Tag', ''):
                non_indexed_urls.add(url)
                status[url] = get_status_code(url) + ' - Non-Indexed'
            else:
                status[url] = get_status_code(url) + ' - Indexed'
        except requests.RequestException:
            status[url] = get_status_code(url) + ' - Error'
    return non_indexed_urls, status

def get_status_code(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return f"Status Code: {response.status_code} ({response.reason})"
    except requests.RequestException as e:
        return f"Status Code: Error ({str(e)})"





from django.contrib.auth.decorators import login_required
from .models import CrawlingResult, UserWebsite


@login_required
def get_user_websites(request):
    try:
        user_website = UserWebsite.objects.get(user=request.user)
        websites = user_website.get_urls()
        return JsonResponse({'websites': websites})
    except UserWebsite.DoesNotExist:
        return JsonResponse({'websites': []})



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated



class CrawlingResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        # Fetch crawling results based on the user
        results = {'message': 'Success', 'user': user.username}
        return Response(results)


# analyze/views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import CrawlingResult
from .serializers import CrawlingResultSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_crawling_results(request):
    user = request.user

    # Check if the user is authenticated
    if not user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Fetch results from the database for the authenticated user
    results = CrawlingResult.objects.filter(user=user)

    # Serialize the data
    serializer = CrawlingResultSerializer(results, many=True)

    # Return the serialized data
    return Response({
        "message": "Success",
        "results": serializer.data
    })

# Error page Analyzise


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

@csrf_exempt
def analyze_websiteinfo(request):
    if request.method == 'GET':
        try:
            # Get the base_url from query parameters
            base_url = request.GET.get('base_url')
            if not base_url:
                return JsonResponse({'error': 'Missing base_url in query parameters'}, status=400)
            
            all_pages = crawl_website(base_url)
            # Analyze every page crawled from the website
            results = {page: analyze_page(page) for page in all_pages}
            return JsonResponse(results)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only GET method is allowed.'}, status=405)

def crawl_website(base_url):
    """Crawl the entire website starting from base_url and return a set of unique URLs."""
    visited_urls = set()  # To keep track of visited URLs
    to_visit = [base_url]  # A list of URLs to visit

    while to_visit:
        url = to_visit.pop(0)
        if url not in visited_urls:
            visited_urls.add(url)  # Mark the URL as visited
            page_content = fetch_content_from_url(url)
            if page_content:
                soup = BeautifulSoup(page_content, 'html.parser')
                # Call get_all_links with the visited_urls to avoid re-crawling
                for link in get_all_links(soup, base_url, visited_urls):
                    if link not in visited_urls:
                        to_visit.append(link)
    return visited_urls

def get_all_links(soup, base_url, visited_urls):
    """Get all internal links from a given BeautifulSoup object (HTML)."""
    links = set()
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        full_url = urljoin(base_url, href)
        # Only add internal links from the same domain
        if urlparse(full_url).netloc == urlparse(base_url).netloc and full_url not in visited_urls:
            links.add(full_url)
    return links

def analyze_page(url):
    """Analyze the contents of a single page and return relevant SEO info."""
    content = fetch_content_from_url(url)
    if not content:
        return {'error': 'Unable to fetch content'}
    
    soup = BeautifulSoup(content, 'html.parser')
    return {
        'url': url,
        'title_tag': analyze_title_tag(soup),
        'title_length': analyze_title_length(soup),
        'meta_description': analyze_meta_description(soup),
        'meta_description_length': analyze_meta_description_length(soup),
        'heading_h1': analyze_heading_h1(soup),
        'heading_h1_length': analyze_heading_h1_length(soup),
    }

def fetch_content_from_url(url):
    """Fetch the HTML content of a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

# Individual SEO analysis functions
def analyze_title_tag(soup):
    title_tags = soup.find_all('title')
    if len(title_tags) == 0:
        return 'error: missing or empty'
    elif len(title_tags) > 1:
        return 'alert: more than one title tag'
    else:
        return 'ok'

def analyze_title_length(soup):
    title_tag = soup.find('title')
    if title_tag:
        title_length = len(title_tag.get_text().strip())
        if 50 <= title_length <= 70:
            return 'ok'
        elif title_length > 70:
            return 'alert: too long'
        elif title_length < 15:
            return 'error: too short'
    return 'error: missing or empty'

def analyze_meta_description(soup):
    meta_descriptions = soup.find_all('meta', attrs={'name': 'description'})
    if len(meta_descriptions) == 0:
        return 'error: missing or empty'
    elif len(meta_descriptions) > 1:
        return 'warning: more than one meta description'
    else:
        return 'ok'

def analyze_meta_description_length(soup):
    meta_description_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_description_tag:
        meta_description = meta_description_tag.get('content', '').strip()
        length = len(meta_description)
        if 100 <= length <= 156:
            return 'ok'
        elif length > 156:
            return 'warning: too long'
        elif length < 100:
            return 'error: too short'
    return 'error: missing or empty'

def analyze_heading_h1(soup):
    h1_tags = soup.find_all('h1')
    if len(h1_tags) == 0:
        return 'error: missing'
    elif len(h1_tags) > 1:
        return 'warning: more than one h1 tag'
    else:
        return 'ok'

def analyze_heading_h1_length(soup):
    h1_tag = soup.find('h1')
    if h1_tag:
        h1_text = h1_tag.get_text().strip()
        length = len(h1_text)
        if 60 <= length <= 100:
            return 'ok'
        elif length > 100:
            return 'warning: too long'
        elif length < 50:
            return 'error: too short'
    return 'error: missing'


#  Website page Loading or Page loading speed code

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

@csrf_exempt
def page_loading_speed(request):
    if request.method == 'GET':
        try:
            # Get the base_url from query parameters instead of request body
            base_url = request.GET.get('base_url')
            if not base_url:
                return JsonResponse({'error': 'Base URL is required.'}, status=400)
            
            all_pages = crawl_website(base_url)
            results = {page: measure_loading_speed(page) for page in all_pages}
            return JsonResponse(results)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only GET method is allowed.'}, status=405)

def crawl_website(base_url):
    visited = set()
    to_visit = [base_url]
    while to_visit:
        url = to_visit.pop(0)
        if url not in visited:
            visited.add(url)
            page_content = fetch_content_from_url(url)
            if page_content:
                soup = BeautifulSoup(page_content, 'html.parser')
                for link in get_all_links(soup, base_url):
                    if link not in visited and link not in to_visit:
                        to_visit.append(link)
    return visited

def get_all_links(soup, base_url):
    links = set()
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        full_url = urljoin(base_url, href)
        # Ensure URL is from the same domain
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(urlparse(full_url)._replace(query='').geturl())  # Normalize URL
    return links

def measure_loading_speed(url):
    start_time = time.time()
    try:
        response = requests.get(url, timeout=100)  # Add a timeout for better control
        response.raise_for_status()
        load_time = time.time() - start_time
        return f"{load_time:.2f} seconds"
    except requests.RequestException:
        return "Failed to load"

def fetch_content_from_url(url):
    try:
        response = requests.get(url, timeout=10)  # Add a timeout for better control
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None
    
#   All issue code or all issueinfo
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from django.http import JsonResponse
from django.views.decorators.http import require_GET

# Analysis functions with consistent signature

def analyze_indexability(soup, headers, url):
    issues = []
    if 'X-Robots-Tag' in headers and 'noindex' in headers['X-Robots-Tag'].lower():
        issues.append('X-Robots-Tag header contains "noindex".')
    if soup.find('meta', {'name': 'robots', 'content': 'noindex'}):
        issues.append('Meta robots tag contains "noindex".')
    return issues, 'Ensure pages that should be indexed do not have "noindex" directives.'

def analyze_crawlability(soup, headers, url):
    issues = []
    if soup.find('meta', {'name': 'robots', 'content': 'nofollow'}):
        issues.append('Meta robots tag contains "nofollow".')
    return issues, 'Ensure pages that should be crawled do not have "nofollow" directives.'

def analyze_redirects(soup, headers, url):
    issues = []
    try:
        response = requests.get(url, allow_redirects=False)
        if 300 <= response.status_code < 400:
            issues.append(f'Redirect detected: {response.status_code} Location: {response.headers.get("Location")}')
    except requests.RequestException as e:
        issues.append(f'Error checking redirects: {str(e)}')
    return issues, 'Avoid unnecessary redirects.'

def analyze_https(soup, headers, url):
    issues = []
    if not url.startswith('https://'):
        issues.append('URL does not use HTTPS.')
    return issues, 'Ensure the site uses HTTPS.'

def analyze_canonicalization(soup, headers, url):
    issues = []
    canonical = soup.find('link', {'rel': 'canonical'})
    if canonical and canonical['href'] != url:
        issues.append(f'Canonical URL mismatch: {canonical["href"]}')
    return issues, 'Ensure the canonical URL is correct.'

def analyze_structured_data(soup, headers, url):
    issues = []
    structured_data = soup.find_all('script', {'type': 'application/ld+json'})
    if not structured_data:
        issues.append('No structured data found.')
    return issues, 'Implement structured data using JSON-LD.'

def analyze_mobile_optimization(soup, headers, url):
    issues = []
    viewport = soup.find('meta', {'name': 'viewport'})
    if not viewport:
        issues.append('Viewport meta tag missing.')
    return issues, 'Ensure the viewport meta tag is present for mobile optimization.'

def analyze_meta_tags(soup, headers, url):
    issues = []
    if not soup.find('meta', {'name': 'description'}):
        issues.append('Meta description tag missing.')
    return issues, 'Add a meta description tag.'

def analyze_headings(soup, headers, url):
    issues = []
    if not soup.find('h1'):
        issues.append('H1 heading missing.')
    return issues, 'Ensure an H1 heading is present.'

def analyze_content_quality(soup, headers, url):
    issues = []
    text_length = len(soup.get_text(strip=True))
    if text_length < 300:
        issues.append('Page content is too short.')
    return issues, 'Ensure sufficient content on the page.'

def analyze_images(soup, headers, url):
    issues = []
    images = soup.find_all('img')
    for img in images:
        if not img.get('alt'):
            issues.append(f'Image with src "{img.get("src")}" is missing alt text.')
    return issues, 'Ensure all images have alt text.'

def analyze_navigation(soup, headers, url):
    issues = []
    nav_links = soup.find_all('a', href=True)
    if not nav_links:
        issues.append('No navigation links found.')
    return issues, 'Ensure navigation links are present.'

def analyze_page_layout(soup, headers, url):
    issues = []
    if not soup.find('header'):
        issues.append('Header element missing.')
    if not soup.find('footer'):
        issues.append('Footer element missing.')
    return issues, 'Ensure header and footer elements are present.'

def analyze_user_interaction(soup, headers, url):
    issues = []
    if not soup.find('button') and not soup.find('a', {'role': 'button'}):
        issues.append('No interactive elements like buttons found.')
    return issues, 'Ensure interactive elements are present.'

def analyze_page_speed(soup, headers, url):
    issues = []
    # Placeholder for page speed analysis
    return issues, 'Optimize page speed.'

def analyze_caching(soup, headers, url):
    issues = []
    try:
        response = requests.get(url)
        if 'Cache-Control' not in response.headers:
            issues.append('Cache-Control header missing.')
    except requests.RequestException as e:
        issues.append(f'Error checking caching: {str(e)}')
    return issues, 'Ensure Cache-Control headers are set.'

def analyze_server_performance(soup, headers, url):
    issues = []
    # Placeholder for server performance analysis
    return issues, 'Optimize server performance.'

def analyze_vulnerabilities(soup, headers, url):
    issues = []
    # Placeholder for vulnerability analysis
    return issues, 'Address any security vulnerabilities.'

def analyze_link_issues(soup, headers, url):
    issues = []
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        full_url = urljoin(url, href)
        try:
            response = requests.get(full_url, timeout=5)
            if response.status_code >= 400:
                issues.append(f'Broken link detected: {full_url} (Status: {response.status_code})')
        except requests.RequestException as e:
            issues.append(f'Error checking link {full_url}: {str(e)}')
    return issues, 'Fix or remove broken links.'

def analyze_accessibility(soup, headers, url):
    issues = []
    if not soup.find('main'):
        issues.append('Main landmark missing.')
    if not soup.find('nav'):
        issues.append('Navigation landmark missing.')
    if not soup.find('footer'):
        issues.append('Footer landmark missing.')
    return issues, 'Ensure presence of main, navigation, and footer landmarks for accessibility.'

def analyze_privacy(soup, headers, url):
    issues = []
    privacy_policies = soup.find_all('a', href=True)
    if not any('privacy' in link['href'].lower() for link in privacy_policies):
        issues.append('Privacy policy link missing.')
    return issues, 'Ensure a privacy policy link is present on the site.'

def analyze_social_media(soup, headers, url):
    issues = []
    social_links = ['facebook.com', 'twitter.com', 'instagram.com']
    links = [a['href'] for a in soup.find_all('a', href=True)]
    for social_link in social_links:
        if not any(social_link in link for link in links):
            issues.append(f'{social_link} link missing.')
    return issues, 'Ensure links to Facebook, Twitter, and Instagram are present.'

def analyze_localization(soup, headers, url):
    issues = []
    lang_tag = soup.find('html', lang=True)
    if not lang_tag:
        issues.append('HTML lang attribute missing.')
    return issues, 'Add an HTML lang attribute for localization.'

def analyze_sitemap_usage(soup, headers, url):
    issues = []
    sitemap_url = urljoin(url, '/sitemap.xml')
    try:
        response = requests.get(sitemap_url)
        if response.status_code != 200:
            issues.append('sitemap.xml file is missing or inaccessible.')
    except requests.RequestException as e:
        issues.append(f'Error checking sitemap.xml: {str(e)}')
    return issues, 'Ensure a sitemap.xml file is present and accessible.'

def analyze_robots_txt(soup, headers, url):
    issues = []
    robots_url = urljoin(url, '/robots.txt')
    try:
        response = requests.get(robots_url)
        if response.status_code != 200:
            issues.append('robots.txt file is missing or inaccessible.')
    except requests.RequestException as e:
        issues.append(f'Error checking robots.txt: {str(e)}')
    return issues, 'Ensure a robots.txt file is present and accessible.'

def analyze_miscellaneous(soup, headers, url):
    issues = []
    # Implement additional miscellaneous checks if necessary
    return issues, 'Add any additional checks relevant to your site.'

# Crawling function

def crawl_site(base_url):
    visited = set()
    to_visit = deque([base_url])
    pages = []

    while to_visit:
        url = to_visit.popleft()
        if url in visited:
            continue
        
        visited.add(url)
        pages.append(url)
        
        try:
            response = requests.get(url)
            response.encoding = response.apparent_encoding  # Handle encoding issues
            soup = BeautifulSoup(response.content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    if full_url not in visited:
                        to_visit.append(full_url)
        except requests.RequestException:
            continue

    return pages

# View function

@require_GET
def errorinfoissue(request):
    base_url = request.GET.get('url')
    if not base_url:
        return JsonResponse({'error': 'URL parameter is required'}, status=400)

    pages = crawl_site(base_url)
    results = {}

    analyses = [
        analyze_indexability,
        analyze_crawlability,
        analyze_redirects,
        analyze_https,
        analyze_canonicalization,
        analyze_structured_data,
        analyze_mobile_optimization,
        analyze_meta_tags,
        analyze_headings,
        analyze_content_quality,
        analyze_images,
        analyze_navigation,
        analyze_page_layout,
        analyze_user_interaction,
        analyze_page_speed,
        analyze_caching,
        analyze_server_performance,
        analyze_vulnerabilities,
        analyze_link_issues,
        analyze_accessibility,
        analyze_privacy,
        analyze_social_media,
        analyze_localization,
        analyze_sitemap_usage,
        analyze_robots_txt,
        analyze_miscellaneous,
    ]

    for url in pages:
        page_results = {}
        try:
            response = requests.get(url)
            response.encoding = response.apparent_encoding  # Handle encoding issues
            soup = BeautifulSoup(response.content, 'html.parser')
            headers = response.headers

            for analysis in analyses:
                issues, fix = analysis(soup, headers, url)
                if issues:
                    page_results[analysis._name_] = {
                        'issues': issues,
                        'fix': fix
                    }
        
        except requests.RequestException as e:
            page_results['error'] = f'Error analyzing {url}: {str(e)}'
        
        results[url] = page_results
    
    return JsonResponse(results)
