from audioop import reverse
from enum import member
from multiprocessing import AuthenticationError
from pyexpat.errors import messages
from types import MemberDescriptorType
from urllib import response
from django.contrib.auth import authenticate, login
from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.test import RequestFactory
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from bs4 import BeautifulSoup
from django.http import JsonResponse

from members.apps import MembersConfig
import json
from django.core.mail import send_mail
import random



import random
from django.core.mail import send_mail
from django.conf import settings





from django.http import JsonResponse
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from django.views.decorators.csrf import csrf_exempt


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

@csrf_exempt
def get_internal_linksonly(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'Missing URL parameter'}, status=400)

    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        internal_links = []
        base_url = urlparse(url).scheme + '://' + urlparse(url).netloc

        for link in links:
            href = link.get('href', '')

            if not href or href.startswith('#'):
                continue

            absolute_url = urljoin(base_url, href)
            parsed_absolute_url = urlparse(absolute_url)
            parsed_base_url = urlparse(base_url)

            if parsed_absolute_url.netloc == parsed_base_url.netloc:
                internal_links.append(absolute_url)

        return JsonResponse({
            'internal_links_count': len(internal_links),
            'internal_links': internal_links
        })
    except requests.RequestException as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)









        
@csrf_exempt
def images(request):
    if request.method == 'GET':
        url = request.GET.get('url', ' ')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all image tags
            image_tags = soup.find_all('img')
            total_images = len(image_tags)

            # Check for broken images
            broken_images = 0
            broken_image_links = []
            valid_image_links = []
            for img in image_tags:
                src = img.get('src')
                if src:
                    img_url = urljoin(url, src)
                    try:
                        img_response = requests.get(img_url)
                        if img_response.status_code != 200:
                            broken_images += 1
                            broken_image_links.append(img_url)
                        else:
                            valid_image_links.append(img_url)
                    except requests.exceptions.RequestException:
                        broken_images += 1
                        broken_image_links.append(img_url)

            # Extract all anchor tags
            anchor_tags = soup.find_all('a')
            total_links = len(anchor_tags)

            # Check for broken links
            broken_links = 0
            broken_link_urls = []
            valid_link_urls = []
            for link in anchor_tags:
                href = link.get('href')
                if href:
                    link_url = urljoin(url, href)
                    try:
                        link_response = requests.get(link_url)
                        if link_response.status_code != 200:
                            broken_links += 1
                            broken_link_urls.append(link_url)
                        else:
                            valid_link_urls.append(link_url)
                    except requests.exceptions.RequestException:
                        broken_links += 1
                        broken_link_urls.append(link_url)

            return JsonResponse({
                'total_images': total_images,
                'broken_images': broken_images,
                'broken_image_links': broken_image_links,
                'valid_image_links': valid_image_links,
                'total_links': total_links,
                'broken_links': broken_links,
                'broken_link_urls': broken_link_urls,
                'valid_link_urls': valid_link_urls,
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
    




@csrf_exempt
def errorlinks(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all anchor tags
            anchor_tags = soup.find_all('a')
            total_links = len(anchor_tags)

            # Check for broken links
            broken_links = {}
            for link in anchor_tags:
                href = link.get('href')
                if href:
                    link_url = urlparse(href)
                    if not link_url.netloc:
                        link_url = urlparse(urljoin(url, href))
                    try:
                        link_response = requests.head(link_url.geturl())
                        if link_response.status_code != 200:
                            broken_links[link_url.geturl()] = link_response.status_code
                    except requests.exceptions.RequestException as e:
                        broken_links[link_url.geturl()] = str(e)

            return JsonResponse({
                'total_links': total_links,
                'broken_links': broken_links,
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)

@csrf_exempt
def analyze_website(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()
                title_length = len(title)
                title_missing = False
                title_too_long = False
                title_too_short = False
            else:
                title_missing = True
                title = ''
                title_length = 0
                title_too_long = False
                title_too_short = False

            if title_missing:
                return JsonResponse({'error': 'Title is missing'}, status=200)
            elif title_length > 70:  # Example threshold for title length
                return JsonResponse({'error': 'Title is too long'}, status=200)
            elif title_length < 10:  # Example threshold for title length
                return JsonResponse({'error': 'Title is too short'}, status=200)
            else:
                pass  # Title is within acceptable limits

            # Extract h1
            h1_tag = soup.find('h1')
            if h1_tag:
                h1 = h1_tag.text.strip()
                h1_missing = False
            else:
                h1_missing = True
                h1 = ''

            if h1_missing:
                return JsonResponse({'error': 'H1 tag is missing'}, status=200)
            else:
                pass  # H1 tag is present

            # Extract meta description
            meta_description_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_description_tag:
                meta_description = meta_description_tag.get('content', '').strip()
                meta_description_length = len(meta_description)
                meta_description_missing = False
            else:
                meta_description_missing = True
                meta_description = ''
                meta_description_length = 0

            if meta_description_missing:
                return JsonResponse({'error': 'Meta description is missing'}, status=200)
            elif meta_description_length > 160:  # Example threshold for meta description length
                return JsonResponse({'error': 'Meta description is too long'}, status=200)
            elif meta_description_length < 70:  # Example threshold for meta description length
                return JsonResponse({'error': 'Meta description is too short'}, status=200)
            else:
                pass  # Meta description is within acceptable limits

            # Check for SERP discrepancies (page name and SERP do not match)
            page_name = title.split(' | ')[0]  # Extracting the page name from the title
            serp = meta_description.split(' | ')[0]  # Extracting the SERP from the meta description
            if page_name.lower() != serp.lower():
                return JsonResponse({'error': 'Page name and SERP do not match'}, status=200)
            else:
                pass  # Page name and SERP match

            # You can add more checks for word count, etc. as needed

            return JsonResponse({'success': 'Page information is consistent'}, status=200)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_title(request):
    if request.method == 'GET':
        base_url = request.GET.get('url', '')
        if not base_url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        visited = set()
        queue = deque([base_url])
        results = []

        while queue:
            url = queue.popleft()
            if url in visited:
                continue

            visited.add(url)
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract SEO data
                title = soup.title.string.strip() if soup.title else None
                h1_tag = soup.find('h1')
                meta_description = None
                meta_tag = soup.find('meta', {'name': 'description'})
                if meta_tag:
                    meta_description = meta_tag.get('content')

                words_count = len(soup.get_text().split())
                issues = {}

                if not title:
                    issues['missing_title'] = 'Title is missing'
                elif len(title) > 70:
                    issues['title_too_long'] = 'Title is too long'
                elif len(title) < 10:
                    issues['title_too_short'] = 'Title is too short'

                if not h1_tag:
                    issues['missing_h1'] = 'H1 tag is missing'

                if not meta_description:
                    issues['missing_meta_description'] = 'Meta description is missing'
                elif len(meta_description) > 160:
                    issues['meta_description_too_long'] = 'Meta description is too long'
                elif len(meta_description) < 50:
                    issues['meta_description_too_short'] = 'Meta description is too short'

                if title and meta_description:
                    serp_title = f"{title} - {meta_description}"
                    if serp_title != soup.title.string.strip():
                        issues['serp_changed'] = 'SERP title and page title/description do not match'

                if words_count < 200:
                    issues['low_word_count'] = 'Word count is significantly low'
                elif words_count > 1000:
                    issues['word_count_changed'] = 'Word count is significantly high'

                results.append({
                    'url': url,
                    'title': title,
                    'h1_tag': h1_tag.string if h1_tag else None,
                    'meta_description': meta_description,
                    'words_count': words_count,
                    'issues': issues
                })

                # Find all links on the current page
                for link in soup.find_all('a', href=True):
                    link_url = urljoin(url, link['href'])
                    if urlparse(base_url).netloc == urlparse(link_url).netloc and link_url not in visited:
                        queue.append(link_url)

            except Exception as e:
                results.append({'url': url, 'error': str(e)})

        return JsonResponse(results, safe=False)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)


@csrf_exempt
def resources(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all resources (images, scripts, stylesheets)
            resources = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    resources.append(src)
            for script in soup.find_all('script', src=True):
                resources.append(script['src'])
            for link in soup.find_all('link', rel='stylesheet', href=True):
                resources.append(link['href'])

            # Initialize issue counters
            too_large_images = 0
            broken_images = 0
            redirecting_images = 0
            missing_alt_text = 0

            # Initialize list to store broken image URLs with alt attribute
            broken_images_with_alt = []

            # Check each resource
            for resource_url in resources:
                try:
                    resource_response = requests.head(resource_url, allow_redirects=True)
                    if resource_response.status_code != 200:
                        if resource_url.endswith('.jpg') or resource_url.endswith('.png') or resource_url.endswith('.gif'):
                            broken_images += 1
                            if 'alt' in resource_url:
                                broken_images_with_alt.append(resource_url)
                        else:
                            redirecting_images += 1
                    else:
                        content_length = int(resource_response.headers.get('content-length', 0))
                        if content_length > 5 * 1024 * 1024:  # 5 MB
                            too_large_images += 1
                except requests.exceptions.RequestException:
                    broken_images += 1

            # Find images with missing alt attribute
            for img in soup.find_all('img'):
                if not img.get('alt'):
                    missing_alt_text += 1

            return JsonResponse({
                'too_large_images': too_large_images,
                'broken_images': broken_images,
                'broken_images_with_alt': len(broken_images_with_alt),
                'redirecting_images': redirecting_images,
                'missing_alt_text': missing_alt_text,
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
    

    
    
@csrf_exempt
def imagesone(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all image tags
            image_tags = soup.find_all('img')
            total_images = len(image_tags)

            # Initialize counters
            broken_images_count = 0
            redirecting_images_count = 0
            pages_with_broken_images = set()
            pages_with_redirecting_images = set()

            for img in image_tags:
                src = img.get('src')
                if src:
                    image_url = urlparse(urljoin(url, src))
                    try:
                        image_response = requests.head(image_url.geturl(), allow_redirects=True)
                        if image_response.status_code != 200:
                            broken_images_count += 1
                            pages_with_broken_images.add(url)
                        elif image_response.history:
                            redirecting_images_count += 1
                            pages_with_redirecting_images.add(url)
                    except requests.exceptions.RequestException:
                        broken_images_count += 1
                        pages_with_broken_images.add(url)

            return JsonResponse({
                'total_images': total_images,
                'broken_images_count': broken_images_count,
                'redirecting_images_count': redirecting_images_count,
                'pages_with_broken_images': list(pages_with_broken_images),
                'pages_with_redirecting_images': list(pages_with_redirecting_images),
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)


@csrf_exempt
def url(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Dictionary to store analysis results for each page
            page_analysis = {}

            # Extract all internal links
            internal_links = set()
            base_url = urlparse(url).scheme + '://' + urlparse(url).netloc
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(url).netloc:
                    internal_links.add(full_url)

            # Analyze each internal link
            for internal_link in internal_links:
                try:
                    internal_response = requests.get(internal_link, allow_redirects=True)
                    internal_response.raise_for_status()
                    internal_soup = BeautifulSoup(internal_response.content, 'html.parser')

                    # Extract page title
                    title = internal_soup.title.string.strip() if internal_soup.title else None

                    # Check for duplicate content
                    if title:
                        if title in page_analysis:
                            page_analysis[title]['duplicate_content'] = True
                        else:
                            page_analysis[title] = {'duplicate_content': False}

                    # Check for orphan pages
                    if not internal_soup.find('a', href=url) and url not in internal_soup.find_all('a', href=True):
                        page_analysis[title]['orphan_page'] = True
                    else:
                        page_analysis[title]['orphan_page'] = False

                    # Check for redirect URLs with status code 200
                    if internal_response.history:
                        page_analysis[title]['redirect_url'] = True
                    else:
                        page_analysis[title]['redirect_url'] = False

                    # Check if the status code is 200
                    if internal_response.status_code == 200:
                        page_analysis[title]['status_code_200'] = True
                    else:
                        page_analysis[title]['status_code_200'] = False

                except requests.exceptions.RequestException:
                    pass  # Skip analyzing the page in case of any request exception

            return JsonResponse({'page_analysis': page_analysis})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
 

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def extract_sitemaps(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all internal links
            internal_links = set()
            base_url = urlparse(url).scheme + '://' + urlparse(url).netloc
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(url).netloc:
                    internal_links.add(full_url)

            # Initialize metrics
            num_sitemaps = 0
            pages_in_sitemaps = set()
            not_indexable_pages_in_sitemaps = set()
            indexable_pages_not_in_sitemaps = set()
            pages_in_multiple_sitemaps = defaultdict(int)
            pages_removed_from_sitemaps = set()
            broken_sitemaps = set()
            sitemap_links = defaultdict(list)  # Dictionary to store the sitemap and its links

            # Analyze each internal link for sitemaps and pages
            for internal_link in internal_links:
                if internal_link.endswith('.xml'):
                    num_sitemaps += 1
                    try:
                        sitemap_response = requests.get(internal_link)
                        sitemap_response.raise_for_status()
                        
                        # Parse the sitemap XML and extract URLs
                        sitemap_xml = ET.fromstring(sitemap_response.content)
                        for elem in sitemap_xml.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                            loc = elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
                            pages_in_sitemaps.add(loc)

                            # Add the URL to the sitemap links dictionary
                            sitemap_links[internal_link].append(loc)

                            # If already in indexable pages, remove, otherwise add
                            path = urlparse(loc).path
                            if path in indexable_pages_not_in_sitemaps:
                                indexable_pages_not_in_sitemaps.remove(path)
                            else:
                                indexable_pages_not_in_sitemaps.add(path)
                    except requests.exceptions.RequestException as e:
                        broken_sitemaps.add(f"{internal_link}: {str(e)}")
                else:
                    # Check for sitemaps within the page content
                    if 'sitemap' in internal_link:
                        try:
                            sitemap_response = requests.get(internal_link)
                            sitemap_response.raise_for_status()
                            
                            # Parse the sitemap XML and extract URLs
                            sitemap_xml = ET.fromstring(sitemap_response.content)
                            for elem in sitemap_xml.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                                loc = elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
                                pages_in_sitemaps.add(loc)
                                sitemap_links[internal_link].append(loc)

                        except requests.exceptions.RequestException as e:
                            broken_sitemaps.add(f"{internal_link}: {str(e)}")

                    # Add logic to check pages against sitemaps
                    path = urlparse(internal_link).path
                    if path in pages_in_sitemaps:
                        pages_removed_from_sitemaps.add(path)
                    else:
                        not_indexable_pages_in_sitemaps.add(path)

            # Pages in multiple sitemaps
            for page in pages_in_sitemaps:
                pages_in_multiple_sitemaps[page] += 1

            # Collect status codes for sitemap links
            sitemap_status = {}
            for sitemap_url in sitemap_links:
                for page in sitemap_links[sitemap_url]:
                    status_code = get_status_code(page)
                    sitemap_status[page] = status_code

            # Prepare the response
            response_data = {
                'num_sitemaps': num_sitemaps,
                'pages_in_sitemaps': {
                    'count': len(pages_in_sitemaps),
                    'urls': list(pages_in_sitemaps)  # List of URLs in sitemaps
                },
                'not_indexable_pages_in_sitemaps': {
                    'count': len(not_indexable_pages_in_sitemaps),
                    'urls': list(not_indexable_pages_in_sitemaps)  # List of not indexable pages
                },
                'indexable_pages_not_in_sitemaps': {
                    'count': len(indexable_pages_not_in_sitemaps),
                    'urls': list(indexable_pages_not_in_sitemaps)  # List of indexable pages not in sitemaps
                },
                'pages_in_multiple_sitemaps': dict(pages_in_multiple_sitemaps),
                'pages_removed_from_sitemaps': list(pages_removed_from_sitemaps),
                'broken_sitemaps': list(broken_sitemaps),
                'sitemap_links': dict(sitemap_links),  # Add the links of pages from sitemaps
                'sitemap_status': sitemap_status,  # Status codes for sitemap pages
                'urls_in_sitemaps': [
                    {
                        'sitemap': sitemap,
                        'urls': sitemap_links[sitemap],
                        'status': {url: sitemap_status.get(url) for url in sitemap_links[sitemap]}
                    } for sitemap in sitemap_links
                ]
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)




@csrf_exempt
def socialtags(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all internal links
            internal_links = set()
            base_url = urlparse(url).scheme + '://' + urlparse(url).netloc
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(url).netloc:
                    internal_links.add(full_url)

            # Initialize counters
            indexable_pages = []
            incomplete_og_tags = []
            incomplete_twitter_cards = []
            pages_missing_social_tags = []

            # Required tags for Open Graph and Twitter
            required_og_tags = ['og:title', 'og:description', 'og:image', 'og:url']
            required_twitter_tags = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']

            # Analyze each internal link
            for internal_link in internal_links:
                try:
                    internal_response = requests.get(internal_link, allow_redirects=True)
                    internal_response.raise_for_status()
                    internal_soup = BeautifulSoup(internal_response.content, 'html.parser')

                    # Extract page title
                    title = internal_soup.title.string.strip() if internal_soup.title else None

                    # Extract Open Graph (og:) tags
                    og_tags = internal_soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
                    og_tag_properties = {tag['property'] for tag in og_tags}

                    # Extract Twitter (twitter:) tags
                    twitter_tags = internal_soup.find_all('meta', property=lambda x: x and x.startswith('twitter:'))
                    twitter_tag_properties = {tag['property'] for tag in twitter_tags}

                    # Determine page categorization
                    if all(tag in og_tag_properties for tag in required_og_tags) and all(tag in twitter_tag_properties for tag in required_twitter_tags):
                        indexable_pages.append({'title': title, 'url': internal_link})
                    else:
                        if not all(tag in og_tag_properties for tag in required_og_tags):
                            incomplete_og_tags.append({'title': title, 'url': internal_link})
                        if not all(tag in twitter_tag_properties for tag in required_twitter_tags):
                            incomplete_twitter_cards.append({'title': title, 'url': internal_link})
                        if not og_tags and not twitter_tags:
                            pages_missing_social_tags.append({'title': title, 'url': internal_link})

                except requests.exceptions.RequestException:
                    pass  # Skip analyzing the page in case of any request exception

            return JsonResponse({
                'indexable_pages': indexable_pages,
                'incomplete_og_tags': incomplete_og_tags,
                'incomplete_twitter_cards': incomplete_twitter_cards,
                'pages_missing_social_tags': pages_missing_social_tags
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
    
    

@csrf_exempt
def find_links_with_status_200(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract all internal links
        internal_links = set()
        base_url = urlparse(url).scheme + '://' + urlparse(url).netloc
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(url).netloc:
                internal_links.add(full_url)

        # Filter internal links with status code 200
        links_with_status_200 = []
        for internal_link in internal_links:
            try:
                internal_response = requests.head(internal_link)
                if internal_response.status_code == 200:
                    links_with_status_200.append(internal_link)
            except requests.exceptions.RequestException:
                pass

        return links_with_status_200

    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

@csrf_exempt
def find_links_with_status_200_in_website(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        links_with_status_200 = find_links_with_status_200(url)

        return JsonResponse({'links_with_status_200': links_with_status_200})

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)

import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
from collections import Counter
import re

@csrf_exempt
def keywords(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text content from website
            text = soup.get_text()

            # Tokenize text into words
            words = re.findall(r'\b\w+\b', text.lower())

            # Count keyword occurrences
            keyword_count = Counter(words)

            # Calculate total word count
            total_words = len(words)

            # Calculate keyword density
            keyword_density = {}
            for word, count in keyword_count.items():
                keyword_density[word] = count / total_words

            # Find primary keyword (most frequent word)
            primary_keyword = max(keyword_count, key=keyword_count.get)

            return JsonResponse({
                'keyword_count': keyword_count,
                'keyword_density': keyword_density,
                'primary_keyword': primary_keyword
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)


from django.http import JsonResponse
from bs4 import BeautifulSoup
import requests

@csrf_exempt
def analyze_page(request):
    if request.method == 'GET':
        url = request.GET.get('url', '')
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract page details
            page_title = soup.title.string if soup.title else None
            meta_description_tag = soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_description_tag['content'] if meta_description_tag else None
            h1_tags = soup.find_all('h1')
            word_count = len(soup.get_text().split())

            # Perform analysis
            analysis_result = {
                'url': url,
                'title_missing': not page_title,
                'title_too_long': len(page_title) > 70 if page_title else False,
                'title_too_short': len(page_title) < 10 if page_title else False,
                'meta_description_missing': not meta_description,
                'meta_description_too_long': len(meta_description) > 160 if meta_description else False,
                'meta_description_too_short': len(meta_description) < 50 if meta_description else False,
                'h1_missing': not h1_tags,
                'low_word_count': word_count < 300,  # Set threshold for low word count
                # Add more analysis for other factors
            }

            return JsonResponse(analysis_result)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
    





import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup

def count_sitemaps(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                sitemaps = soup.find_all('sitemap')

                return JsonResponse({'count': len(sitemaps)})
            else:
                return JsonResponse({'error': 'Failed to fetch URL'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    



    import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup

def analyze_canonical_urls(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Fetch the HTML content of the provided URL
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all canonical URLs in the HTML content
                canonical_tags = soup.find_all('link', rel='canonical')

                analysis_result = {
                    'canonicalized': [],
                    'modified': [],
                    'self_canonical': [],
                    'not_set': [],
                    'to_not_found': [],
                    'to_other_client_errors': [],
                    'to_server_errors': [],
                    'to_redirect': [],
                    'to_non_canonical': []
                }

                for tag in canonical_tags:
                    canonical_url = tag.get('href')

                    if not canonical_url:
                        analysis_result['not_set'].append(canonical_url)
                        continue

                    # Check the status code of the canonical URL
                    canonical_response = requests.head(canonical_url)
                    status_code = canonical_response.status_code

                    # Analyze different aspects based on status code
                    if status_code == 200:
                        analysis_result['self_canonical'].append(canonical_url)
                    elif status_code == 404:
                        analysis_result['to_not_found'].append(canonical_url)
                    elif status_code >= 400 and status_code < 500:
                        analysis_result['to_other_client_errors'].append(canonical_url)
                    elif status_code >= 500 and status_code < 600:
                        analysis_result['to_server_errors'].append(canonical_url)
                    elif status_code >= 300 and status_code < 400:
                        analysis_result['to_redirect'].append(canonical_url)
                    else:
                        analysis_result['to_non_canonical'].append(canonical_url)

                return JsonResponse({'analysis_result': analysis_result})
            else:
                return JsonResponse({'error': 'Failed to fetch URL'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    








    import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
import re

def analyze_content(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Fetch the HTML content of the provided URL
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract title and meta description
                title_tag = soup.find('title')
                meta_description_tag = soup.find('meta', attrs={'name': 'description'})

                # Analyze title
                title = title_tag.text.strip() if title_tag else None
                title_length = len(title) if title else 0
                title_missing = True if not title else False
                title_too_long = True if title_length > 70 else False
                title_too_short = True if title_length < 10 else False
                title_changed = False
                title_link = None

                # Analyze meta description
                meta_description = meta_description_tag.get('content').strip() if meta_description_tag else None
                meta_description_length = len(meta_description) if meta_description else 0
                meta_description_missing = True if not meta_description else False
                meta_description_too_long = True if meta_description_length > 160 else False
                meta_description_too_short = True if meta_description_length < 50 else False
                meta_description_changed = False
                meta_description_link = None

                # Extract H1 tag
                h1_tag = soup.find('h1')
                h1_missing = True if not h1_tag else False
                h1_changed = False
                h1_link = None

                # Analyze word count
                text = soup.get_text()
                word_count = len(re.findall(r'\b\w+\b', text))
                low_word_count = True if word_count < 300 else False
                word_count_changed = False
                word_count_link = None

                # Analyze SERP
                serp_changed = False
                page_name_serp_match = False

                # Check if title and meta description match page name
                page_name = url.split('/')[-1]
                if title and page_name in title:
                    page_name_serp_match = True

                return JsonResponse({
                    'title_missing': {'present': title_missing, 'link': url if title_missing else None},
                    'title_too_long': {'present': title_too_long, 'link': url if title_too_long else None},
                    'title_too_short': {'present': title_too_short, 'link': url if title_too_short else None},
                    'title_changed': {'present': title_changed, 'link': title_link},
                    'h1_missing': {'present': h1_missing, 'link': url if h1_missing else None},
                    'h1_changed': {'present': h1_changed, 'link': h1_link},
                    'low_word_count': {'present': low_word_count, 'link': url if low_word_count else None},
                    'word_count_changed': {'present': word_count_changed, 'link': word_count_link},
                    'meta_description_missing': {'present': meta_description_missing, 'link': url if meta_description_missing else None},
                    'meta_description_too_long': {'present': meta_description_too_long, 'link': url if meta_description_too_long else None},
                    'meta_description_too_short': {'present': meta_description_too_short, 'link': url if meta_description_too_short else None},
                    'meta_description_changed': {'present': meta_description_changed, 'link': meta_description_link},
                    'serp_changed': serp_changed,
                    'page_name_serp_match': page_name_serp_match
                })

            else:
                return JsonResponse({'error': 'Failed to fetch URL'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def analyze_resources(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        def fetch_page(url):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return response.text
                else:
                    return None
            except Exception as e:
                return None

        def extract_links(html, base_url):
            soup = BeautifulSoup(html, 'html.parser')
            links = set()
            for tag in soup.find_all('a', href=True):
                href = tag['href']
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    links.add(full_url)
            return links

        def analyze_page(url, visited_urls):
            html = fetch_page(url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')
            resource_tags = soup.find_all(['link', 'script', 'img'])
            all_resources = []
            too_large_images = []
            broken_images = []
            redirecting_images = []
            alternative_text_missing_pages = []
            total_images = 0
            image_links = []

            for tag in resource_tags:
                if tag.name == 'img':
                    img_src = tag.get('src')
                    if img_src:
                        total_images += 1
                        img_src = urljoin(url, img_src)
                        img_response = requests.head(img_src, allow_redirects=True)
                        img_size = int(img_response.headers.get('content-length', 0)) if img_response.headers.get('content-length') else 0
                        if img_size > 1048576:
                            too_large_images.append(img_src)
                        if img_response.status_code != 200:
                            broken_images.append(img_src)
                        if img_response.status_code >= 300 and img_response.status_code < 400:
                            redirecting_images.append(img_src)
                        image_links.append(img_src)
                        if not tag.get('alt'):
                            alternative_text_missing_pages.append(url)
                elif tag.name == 'link' and tag.get('rel') == 'stylesheet':
                    css_href = tag.get('href')
                    if css_href:
                        css_href = urljoin(url, css_href)
                        all_resources.append(css_href)
                elif tag.name == 'script':
                    script_src = tag.get('src')
                    if script_src:
                        script_src = urljoin(url, script_src)
                        all_resources.append(script_src)

            return {
                'all_resources': all_resources,
                'total_images': total_images,
                'image_links': image_links,
                'too_large_images': too_large_images,
                'broken_images': broken_images,
                'redirecting_images': redirecting_images,
                'alternative_text_missing_pages': alternative_text_missing_pages
            }

        visited_urls = set()
        urls_to_visit = set([url])
        results = {
            'all_resources': [],
            'total_images': 0,
            'image_links': [],
            'too_large_images': [],
            'broken_images': [],
            'redirecting_images': [],
            'alternative_text_missing_pages': []
        }

        while urls_to_visit:
            current_url = urls_to_visit.pop()
            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)

            page_results = analyze_page(current_url, visited_urls)
            if page_results:
                results['all_resources'].extend(page_results['all_resources'])
                results['total_images'] += page_results['total_images']
                results['image_links'].extend(page_results['image_links'])
                results['too_large_images'].extend(page_results['too_large_images'])
                results['broken_images'].extend(page_results['broken_images'])
                results['redirecting_images'].extend(page_results['redirecting_images'])
                results['alternative_text_missing_pages'].extend(page_results['alternative_text_missing_pages'])

                links = extract_links(fetch_page(current_url), current_url)
                urls_to_visit.update(links - visited_urls)

        return JsonResponse(results)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)




import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def analyze_links(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Fetch the HTML content of the provided URL
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all links in the HTML content
                link_tags = soup.find_all('a')

                # Initialize variables for analysis
                all_links = set()
                crawled_links = set()
                external_links = set()
                index_urls = set()
                non_index_urls = set()
                do_follow_links = set()
                no_follow_links = set()

                # Extract the base domain of the provided URL
                base_url = urlparse(url).netloc

                # Analyze each link
                for tag in link_tags:
                    # Extract the URL of the link
                    link_url = tag.get('href')
                    if link_url:
                        absolute_url = urljoin(url, link_url)
                        all_links.add(absolute_url)

                        # Check if the link is internal or external
                        parsed_url = urlparse(absolute_url)
                        if parsed_url.netloc == base_url:
                            crawled_links.add(absolute_url)
                        else:
                            external_links.add(absolute_url)

                        # Check if the link is indexable or non-indexable
                        rel_attribute = tag.get('rel', [])
                        if 'nofollow' in rel_attribute:
                            no_follow_links.add(absolute_url)
                        else:
                            do_follow_links.add(absolute_url)

                        # Check if the link leads to an indexable or non-indexable URL
                        if 'noindex' in rel_attribute:
                            non_index_urls.add(absolute_url)
                        else:
                            index_urls.add(absolute_url)

                # Uncrawled links are the difference between all_links and crawled_links
                uncrawled_links = all_links - crawled_links

                return JsonResponse({
                    'all_links': list(all_links),
                    'crawled_links': list(crawled_links),
                    'uncrawled_links': list(uncrawled_links),
                    'external_links': list(external_links),
                    'index_urls': list(index_urls),
                    'non_index_urls': list(non_index_urls),
                    'do_follow_links': list(do_follow_links),
                    'no_follow_links': list(no_follow_links)
                })

            else:
                return JsonResponse({'error': 'Failed to fetch URL'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    






import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup

# List of common social media platforms and their URL identifiers
SOCIAL_MEDIA_PLATFORMS = {
    'instagram': 'instagram.com',
    'whatsapp': 'wa.me',  # WhatsApp links use wa.me
    'linkedin': 'linkedin.com',
    'x': 'twitter.com',  # X still uses twitter.com URLs
    'youtube': 'youtube.com'  # YouTube URL identifier
}

def analyze_social_tags_info(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Fetch the HTML content of the provided URL
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Initialize variables for analysis
                pages_with_social_tags = []
                pages_without_social_tags = []
                social_tag_links = {platform: [] for platform in SOCIAL_MEDIA_PLATFORMS}

                # Search for <a> tags that link to social media platforms
                anchor_tags = soup.find_all('a', href=True)
                for tag in anchor_tags:
                    href = tag['href']
                    for platform, identifier in SOCIAL_MEDIA_PLATFORMS.items():
                        if identifier in href:
                            social_tag_links[platform].append(href)

                # Also check for meta tags with social links (e.g., X/Twitter often in <meta> tags)
                meta_tags = soup.find_all('meta', property=lambda x: x and ('og:' in x or 'twitter:' in x))
                for meta_tag in meta_tags:
                    tag_content = meta_tag.get('content')
                    if tag_content:
                        for platform, identifier in SOCIAL_MEDIA_PLATFORMS.items():
                            if identifier in tag_content:
                                social_tag_links[platform].append(tag_content)

                # Check for pages with and without social tags
                has_social_tags = any(social_tag_links[platform] for platform in SOCIAL_MEDIA_PLATFORMS)
                if has_social_tags:
                    pages_with_social_tags.append(url)
                else:
                    pages_without_social_tags.append(url)

                # Filter out empty entries from social_tag_links
                filtered_social_tag_links = {platform: links for platform, links in social_tag_links.items() if links}

                return JsonResponse({
                    'pages_with_social_tags': pages_with_social_tags,
                    'pages_without_social_tags': pages_without_social_tags,
                    'social_tag_links': filtered_social_tag_links  # Filtered social tag links
                })

            else:
                return JsonResponse({'error': 'Failed to fetch URL'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    



  


def find_duplicate_content(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Fetch the HTML content of the provided URL
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract the visible text content from the HTML
                visible_text = soup.get_text().strip()

                # Split the text into individual words and remove duplicates
                words = visible_text.split()
                unique_words = set(words)

                # Calculate the percentage of unique words compared to total words
                if words:
                    duplicate_percentage = ((len(words) - len(unique_words)) / len(words)) * 100
                else:
                    duplicate_percentage = 0

                return JsonResponse({
                    'duplicate_content_percentage': duplicate_percentage
                })

            else:
                return JsonResponse({'error': 'Failed to fetch URL'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    







import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import nltk
nltk.download('punkt')
nltk.download('stopwords')

def keyword_suggestion(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Fetch the HTML content of the provided URL
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract the visible text content from the HTML
                visible_text = soup.get_text().strip()

                # Tokenize the text into words
                words = word_tokenize(visible_text)

                # Filter out stopwords (common words with little semantic value)
                stop_words = set(stopwords.words('english'))
                filtered_words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]

                # Calculate word frequency distribution
                fdist = FreqDist(filtered_words)

                # Get the most common keywords
                top_keywords = fdist.most_common(10)

                return JsonResponse({
                    'keywords': top_keywords
                })

            else:
                return JsonResponse({'error': 'Failed to fetch URL'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)











import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup

def site_audit(request):
    if request.method == 'GET':
        url = request.GET.get('url')
        if not url:
            return JsonResponse({'error': 'URL parameter is missing'}, status=400)
        
        try:
            audit_results = perform_site_audit(url)
            return JsonResponse(audit_results)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def perform_site_audit(url):
    # Here you would implement your site auditing logic
    # This is a basic example, more checks can be added based on requirements
    
    # Send a request to the URL to fetch the HTML content
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Failed to fetch URL: {response.status_code}')

    # Initialize audit results dictionary
    audit_results = {
        'url': url,
        'status_code': response.status_code,
        'meta_description': '',
        'title_tag': '',
        'headings': {
            'h1': [],
            'h2': [],
            'h3': [],
        },
        'internal_links': [],
        'external_links': [],
        'images': [],
    }

    # Parse HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract meta description
    meta_description_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_description_tag:
        audit_results['meta_description'] = meta_description_tag.get('content')

    # Extract title tag
    title_tag = soup.find('title')
    if title_tag:
        audit_results['title_tag'] = title_tag.text.strip()

    # Extract headings
    for heading_level in range(1, 4):
        heading_tags = soup.find_all(f'h{heading_level}')
        audit_results['headings'][f'h{heading_level}'] = [heading.text.strip() for heading in heading_tags]

    # Extract internal and external links
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            if href.startswith('http'):
                audit_results['external_links'].append(href)
            else:
                audit_results['internal_links'].append(href)

    # Extract images
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            audit_results['images'].append(src)

    return audit_results





import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
import datetime

def analyze_optimization(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Ensure URL starts with http:// or https://
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Indexability Check
                meta_robots_tag = soup.find('meta', attrs={'name': 'robots'})
                if meta_robots_tag:
                    content = meta_robots_tag.get('content', '')
                    indexability = 'Non Indexable' if 'noindex' in content else 'Indexable'
                else:
                    indexability = 'Indexable (No meta robots tag found)'

                # Page Speed Check
                start_time = datetime.datetime.now()
                requests.get(url)  # Trigger the request again for timing
                end_time = datetime.datetime.now()
                page_load_time = (end_time - start_time).total_seconds()

                # Mobile Friendliness Check (Basic Check)
                viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
                mobile_friendly = 'Yes' if viewport_tag else 'No'

                # Secure Connection Check
                secure_connection = 'Yes' if url.startswith('https://') else 'No'

                return JsonResponse({
                    'indexability': indexability,
                    'page_load_time': f'{page_load_time} seconds',
                    'mobile_friendly': mobile_friendly,
                    'secure_connection': secure_connection
                })

            else:
                return JsonResponse({'error': 'Failed to fetch URL'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    


    

from django.http import JsonResponse
from bs4 import BeautifulSoup
import json

def validate_schema_markup(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Ensure URL starts with http:// or https://
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find JSON-LD schema markup
                json_ld_schemas = []
                for script_tag in soup.find_all('script', type='application/ld+json'):
                    try:
                        json_ld_data = json.loads(script_tag.string)
                        json_ld_schemas.append(json_ld_data)
                    except json.JSONDecodeError as e:
                        json_ld_schemas.append({'error': str(e), 'content': script_tag.string})

                # Find microdata schema markup
                microdata_schemas = []
                for item in soup.find_all(attrs={'itemscope': True}):
                    schema = {}
                    if 'itemtype' in item.attrs:
                        schema['type'] = item.attrs['itemtype']
                    properties = {}
                    for prop in item.find_all(attrs={'itemprop': True}):
                        prop_name = prop.attrs['itemprop']
                        prop_value = prop.get('content', prop.text)
                        properties[prop_name] = prop_value
                    schema['properties'] = properties
                    microdata_schemas.append(schema)

                return JsonResponse({
                    'json_ld_schemas': json_ld_schemas,
                    'microdata_schemas': microdata_schemas
                })

            else:
                return JsonResponse({'error': 'Failed to fetch URL'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    




    import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin, urlparse
from collections import deque

def crawl_website(start_url, max_depth=2):
    visited = set()
    queue = deque([(start_url, 0)])
    image_urls = set()

    while queue:
        current_url, depth = queue.popleft()
        if depth > max_depth:
            continue
        
        if current_url in visited:
            continue

        visited.add(current_url)
        
        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all image tags
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src:
                        img_url = urljoin(current_url, src)
                        image_urls.add(img_url)
                
                # Find all links to crawl further
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    full_url = urljoin(current_url, href)
                    
                    # Avoid re-crawling and ensure we only follow links within the same domain
                    if urlparse(full_url).netloc == urlparse(start_url).netloc:
                        queue.append((full_url, depth + 1))
                        
        except requests.RequestException as e:
            print(f"Error fetching {current_url}: {e}")

    return image_urls

import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin, urlparse
from collections import deque

def crawl_website(start_url, max_depth=2):
    visited = set()
    queue = deque([(start_url, 0)])
    image_urls = set()

    while queue:
        current_url, depth = queue.popleft()
        if depth > max_depth:
            continue
        
        if current_url in visited:
            continue

        visited.add(current_url)
        
        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all image tags
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src:
                        img_url = urljoin(current_url, src)
                        image_urls.add(img_url)
                
                # Find all links to crawl further
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    full_url = urljoin(current_url, href)
                    
                    # Avoid re-crawling and ensure we only follow links within the same domain
                    if urlparse(full_url).netloc == urlparse(start_url).netloc:
                        queue.append((full_url, depth + 1))
                        
        except requests.RequestException as e:
            print(f"Error fetching {current_url}: {e}")

    return image_urls

def check_image_optimization(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Ensure URL starts with http:// or https://
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            # Crawl the website to find all image URLs
            image_urls = crawl_website(url)

            results = []
            
            for img_url in image_urls:
                try:
                    # Fetch the image
                    img_response = requests.get(img_url)
                    img_response.raise_for_status()
                    
                    # Check image dimensions
                    image = Image.open(BytesIO(img_response.content))
                    width, height = image.size
                    
                    # Check file size (in KB)
                    file_size = len(img_response.content) / 1024

                    # Determine if dimensions and file size are optimized
                    dimensions_optimized = (width <= 1920 and height <= 1080)
                    file_size_optimized = (file_size <= 200)  # Example threshold

                    results.append({
                        'src': img_url,
                        'width': width,
                        'height': height,
                        'file_size_kb': round(file_size, 2),
                        'dimensions_optimized': dimensions_optimized,
                        'file_size_optimized': file_size_optimized
                    })

                except Exception as e:
                    results.append({
                        'src': img_url,
                        'error': str(e)
                    })

            return JsonResponse({'images': results})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    





    import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
from textstat import textstat
import spacy
from collections import Counter
from urllib.parse import urljoin, urlparse
from collections import deque

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join(p.get_text() for p in paragraphs)
    return text

def extract_headings_text(soup):
    headings_text = ' '.join([heading.get_text() for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
    return headings_text

def analyze_content_quality(text, headings_text):
    # Calculate readability scores
    readability_scores = {
        'flesch_reading_ease': textstat.flesch_reading_ease(text),
        'smog_index': textstat.smog_index(text),
        'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
        'coleman_liau_index': textstat.coleman_liau_index(text),
        'automated_readability_index': textstat.automated_readability_index(text),
        'dale_chall_readability_score': textstat.dale_chall_readability_score(text),
        'difficult_words': textstat.difficult_words(text),
        'linsear_write_formula': textstat.linsear_write_formula(text),
        'gunning_fog': textstat.gunning_fog(text),
    }

    # Extract keywords using spaCy
    doc = nlp(text)
    nouns = [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    
    # Extract keywords from headings
    heading_doc = nlp(headings_text)
    heading_nouns = [token.text.lower() for token in heading_doc if token.pos_ in ['NOUN', 'PROPN']]

    # Count the frequency of each noun in the text and headings
    noun_freq = Counter(nouns)
    heading_noun_freq = Counter(heading_nouns)

    # Determine primary keyword as the most frequent noun in headings
    primary_keyword = heading_noun_freq.most_common(1)[0][0] if heading_noun_freq else None

    return {
        'readability_scores': readability_scores,
        'primary_keyword': primary_keyword,
        'top_keywords': noun_freq.most_common(10)
    }

def crawl_website(start_url, max_depth=2):
    visited = set()
    queue = deque([(start_url, 0)])
    results = {}

    while queue:
        current_url, depth = queue.popleft()
        if depth > max_depth:
            continue
        
        if current_url in visited:
            continue

        visited.add(current_url)
        
        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract page title
                title = soup.title.get_text() if soup.title else 'No Title'
                
                # Extract content and headings
                content = extract_text_from_html(response.text)
                headings_text = extract_headings_text(soup)
                
                # Analyze content quality
                analysis_result = analyze_content_quality(content, headings_text)
                
                # Store results with page title
                results[title] = analysis_result

                # Find all links to crawl further
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    full_url = urljoin(current_url, href)
                    
                    # Avoid re-crawling and ensure we only follow links within the same domain
                    if urlparse(full_url).netloc == urlparse(start_url).netloc:
                        queue.append((full_url, depth + 1))
                        
        except requests.RequestException as e:
            print(f"Error fetching {current_url}: {e}")

    return results

def content_quality_analysis(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Ensure URL starts with http:// or https://
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            # Crawl the website to get content and headings
            results = crawl_website(url)

            return JsonResponse(results)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    




    


import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import analyze_urlinfo, compare_seo_data

logger = logging.getLogger(__name__)


@csrf_exempt
def competitor_analysis(request):
    if request.method == 'GET':
        user_url = request.GET.get('user_url')
        competitor_url = request.GET.get('competitor_url')

        logger.info(f"Received user_url: {user_url}, competitor_url: {competitor_url}")

        if not user_url or not competitor_url:
            logger.error("Missing URLs in the request")
            return JsonResponse({'error': 'Invalid input, URLs are required'}, status=400)

        try:
            # Log URLs being processed
            logger.info(f"Analyzing user URL: {user_url}")
            logger.info(f"Analyzing competitor URL: {competitor_url}")
            
            user_data = analyze_urlinfo(user_url)  # Corrected usage
            competitor_data = analyze_urlinfo(competitor_url)

            logger.info("Comparison of SEO data starting")
            analysis_result = compare_seo_data(user_data, competitor_data)

            # Log success
            logger.info("SEO comparison complete")
            return JsonResponse(analysis_result, status=200)

        except Exception as e:
            # Log the exception details
            logger.error(f"Error occurred: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def analyze_url(url):
    # Example implementation: fetch and analyze the URL content
    try:
        # Fetch the URL content (simplified example)
        response = requests.get(url)
        if response.status_code == 200:
            # Process the response content
            # This is just an example; adjust the parsing as needed
            page_content = response.text
            return {
                'title': extract_title(page_content),
                'description': extract_description(page_content),
                # Add other analysis data as needed
            }
        else:
            return None
    except Exception as e:
        # Handle exceptions
        print(f"Error analyzing URL {url}: {e}")
        return None

def extract_title(html):
    # Dummy implementation for extracting title
    # Replace with actual HTML parsing logic
    return "Extracted Title"

def extract_description(html):
    # Dummy implementation for extracting description
    # Replace with actual HTML parsing logic
    return "Extracted Description"


# snippet_checker/views.py
import requests
from bs4 import BeautifulSoup
import json
from django.http import JsonResponse

def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def check_snippets(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'URL parameter is required'}, status=400)
    
    html_content = fetch_page(url)
    if not html_content:
        return JsonResponse({'error': 'Failed to fetch the page content'}, status=500)

    soup = BeautifulSoup(html_content, 'lxml')
    snippets = {}

    # Regular Snippets
    title = soup.title.string if soup.title else None
    meta_description = soup.find('meta', attrs={'name': 'description'})
    meta_description_content = meta_description['content'] if meta_description and 'content' in meta_description.attrs else None

    if title and meta_description_content:
        snippets['Regular Snippets'] = {
            'Title Tag': title,
            'Meta Description': meta_description_content
        }

    # Rich Snippets (Structured Data using Schema.org)
    structured_data = soup.find_all('script', type='application/ld+json')
    if structured_data:
        snippets['Rich Snippets'] = []
        for data in structured_data:
            try:
                json_data = json.loads(data.string)
                snippets['Rich Snippets'].append(json_data)
            except json.JSONDecodeError:
                continue

    # Featured Snippets (Paragraph, List, Table)
    featured_snippets = []
    if soup.find_all('p'):
        featured_snippets.append('Paragraph')
    if soup.find_all('ol') or soup.find_all('ul'):
        featured_snippets.append('List')
    if soup.find_all('table'):
        featured_snippets.append('Table')
    
    if featured_snippets:
        snippets['Featured Snippets'] = featured_snippets

    # Video Snippets
    video_meta = soup.find('meta', attrs={'property': 'og:video'})
    if video_meta and 'content' in video_meta.attrs:
        snippets['Video Snippets'] = {
            'Video URL': video_meta['content']
        }

    # Image Snippets
    image_meta = soup.find('meta', attrs={'property': 'og:image'})
    if image_meta and 'content' in image_meta.attrs:
        snippets['Image Snippets'] = {
            'Image URL': image_meta['content']
        }

    # Local Pack (Local Snippets)
    address = soup.find('span', attrs={'class': 'local-address'})
    phone = soup.find('span', attrs={'class': 'local-phone'})
    if address and phone:
        snippets['Local Pack'] = {
            'Address': address.text.strip(),
            'Phone': phone.text.strip()
        }

    # Knowledge Graph Snippets
    knowledge_graph = soup.find('div', attrs={'class': 'knowledge-graph'})
    if knowledge_graph:
        snippets['Knowledge Graph Snippets'] = knowledge_graph.text.strip()

    # People Also Ask (PAA) Snippets
    paa_boxes = soup.find_all('div', attrs={'class': 'paa'})
    if paa_boxes:
        snippets['People Also Ask'] = [paa_box.text.strip() for paa_box in paa_boxes]

    return JsonResponse(snippets)




# All Is







# views.py
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def check_website(request):
 
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'URL parameter is missing'}, status=400)

    result = {}
    
    # Check website accessibility
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result['accessibility'] = 'The webpage is accessible'
        else:
            result['accessibility'] = 'The server refused access to your webpages'
    except requests.exceptions.Timeout:
        result['accessibility'] = 'Your site\'s server response time is more than 5 seconds'
    except requests.exceptions.RequestException as e:
        result['accessibility'] = f'An error occurred while trying to access the webpage: {str(e)}'

    # Check DNS resolution
    try:
        requests.get(url, timeout=5)
        result['dns'] = 'The webpage is accessible'
    except requests.exceptions.ConnectionError:
        result['dns'] = 'DNS resolution error. Please contact your web hosting technical support and ask them to investigate and fix the issue.'
    except requests.exceptions.RequestException as e:
        result['dns'] = f'An error occurred while trying to access the webpage: {str(e)}'

    return JsonResponse(result)








import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from requests.exceptions import RequestException

MAX_PAGES = 100  # Limit the number of pages to crawl

def is_broken_link(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code >= 400
    except RequestException:
        return True

def get_page_links(url):
    try:
        response = requests.get(url, timeout=10)  # Increased timeout
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'No title'
        links = set()
        for tag in soup.find_all('a', href=True):
            href = urljoin(url, tag['href'])
            parsed_href = urlparse(href)
            if parsed_href.scheme in ('http', 'https'):
                links.add(href)
        return title, links
    except RequestException as e:
        print(f"Error fetching {url}: {e}")
        return 'Error fetching page', set()



import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from requests.exceptions import RequestException

def get_page_links(url):
    try:
        response = requests.get(url)  # Increased timeout
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else 'No title'
        
        # Extract canonical URL
        canonical_tag = soup.find('link', rel='canonical')
        canonical_url = canonical_tag['href'] if canonical_tag else url
        
        # Extract all links
        links = set()
        for tag in soup.find_all('a', href=True):
            href = urljoin(url, tag['href'])
            parsed_href = urlparse(href)
            if parsed_href.scheme in ('http', 'https'):
                links.add(href)
        
        return title, canonical_url, links
    except RequestException as e:
        print(f"Error fetching {url}: {e}")
        return 'Error fetching page', url, set()

@require_http_methods(["GET"])
def analyze_seotool(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'URL parameter is missing'}, status=400)

    try:
        pages_to_crawl = {url}
        crawled_pages = {}
        visited_pages = set()
        
        while pages_to_crawl:
            page = pages_to_crawl.pop()
            if page in visited_pages:
                continue
            visited_pages.add(page)
            title, canonical_url, links = get_page_links(page)
            if title:
                crawled_pages[page] = {'title': title, 'canonical_url': canonical_url, 'links': links}
                pages_to_crawl.update(links - visited_pages)

        # Analyze each page
        non_canonical_links = []
        for page, data in crawled_pages.items():
            title = data['title']
            canonical_url = data['canonical_url']
            links = data['links']

            non_canonical_links_on_page = [
                link for link in links
                if link != canonical_url and urlparse(link).netloc == urlparse(page).netloc
            ]

            if non_canonical_links_on_page:
                non_canonical_links.append({
                    'page': page,
                    'title': title,
                    'non_canonical_links': non_canonical_links_on_page
                })

        return JsonResponse(non_canonical_links, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'message': 'An error occurred while trying to analyze the webpage', 'error': str(e)}, status=500)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import re
import time
from collections import defaultdict

@csrf_exempt
def seo_analysis(request):
    if request.method == 'GET':
        url = request.GET.get('url')
        if not url:
            return JsonResponse({"errors": ["No URL provided"]}, status=400)

        visited_pages = {}  # Change from set to dict
        results = defaultdict(list)
        security_headers = [
            "Strict-Transport-Security", "Content-Security-Policy",
            "X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection"
        ]

        def crawl_page(page_url):
            if page_url in visited_pages:
                return
            start_time = time.time()
            try:
                response = requests.get(page_url)
                response_time = time.time() - start_time
            except requests.RequestException as e:
                results["errors"].append(f"Error fetching {page_url}: {str(e)}")
                return

            soup = BeautifulSoup(response.content, 'html.parser')

            if response.status_code >= 400:
                results["errors"].append(
                    f"Client/Server Error with status code: {response.status_code} on URL: {page_url}"
                )

            if response.status_code == 404:
                results["broken_links"].append(page_url)

            try:
                response_history = requests.head(page_url, allow_redirects=True).history
                results["redirects"].extend(
                    [{"url": r.url, "status_code": r.status_code} for r in response_history]
                )
            except requests.RequestException as e:
                results["errors"].append(f"Error checking redirects for {page_url}: {str(e)}")

            headers = {header: response.headers.get(header) for header in security_headers}
            results["security"].append({page_url: headers})

            for a in soup.find_all('a', href=True):
                link = a['href']
                if not link.startswith(urlparse(url).scheme + '://' + urlparse(url).netloc):
                    try:
                        link_response = requests.head(link)
                        results["external_links"].append(
                            {'link': link, 'status_code': link_response.status_code, 'source_page': page_url}
                        )
                    except requests.RequestException:
                        results["external_links"].append(
                            {'link': link, 'status_code': 'No Response', 'source_page': page_url}
                        )

            internal_links = []
            for a in soup.find_all('a', href=True):
                link = urljoin(page_url, a['href'])
                if link.startswith(urlparse(url).scheme + '://' + urlparse(url).netloc):
                    internal_links.append(link)
                    try:
                        link_response = requests.head(link)
                        if link_response.status_code == 404:
                            results["broken_internal_links"].append(link)
                    except requests.RequestException:
                        results["broken_internal_links"].append(link)

            results["internal_links"].extend(internal_links)

            if not re.match(r'^[a-zA-Z0-9_\-\/:]+$', page_url):
                results["url_issues"].append(f'URL contains non-ASCII characters: {page_url}')
            if '_' in page_url:
                results["url_issues"].append(f'URL contains underscores: {page_url}')
            if any(c.isupper() for c in page_url):
                results["url_issues"].append(f'URL contains uppercase characters: {page_url}')
            if len(page_url) > 2000:
                results["url_issues"].append(f'URL is too long: {page_url}')

            title = soup.title.string if soup.title else None
            if not title:
                results["page_titles"].append(f"Missing title on URL: {page_url}")
            elif len(title) > 60:
                results["page_titles"].append(f"Title is too long on URL: {page_url}")
            elif len(title) < 10:
                results["page_titles"].append(f"Title is too short on URL: {page_url}")

            meta_description = soup.find('meta', attrs={'name': 'description'})
            description_content = meta_description['content'] if meta_description and 'content' in meta_description.attrs else None
            if not description_content:
                results["meta_description"].append(f"Missing meta description on URL: {page_url}")
            elif len(description_content) > 160:
                results["meta_description"].append(f"Meta description is too long on URL: {page_url}")
            elif len(description_content) < 50:
                results["meta_description"].append(f"Meta description is too short on URL: {page_url}")

            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords_content = meta_keywords['content'] if meta_keywords and 'content' in meta_keywords.attrs else None
            results["meta_keywords"].append(keywords_content if keywords_content else "Missing meta keywords")

            results["file_size"].append({page_url: response.headers.get('Content-Length', 'Unknown')})

            results["response_time"].append({"url": page_url, "response_time": response_time})

            last_modified = response.headers.get('Last-Modified')
            results["last_modified"].append({page_url: last_modified if last_modified else "Missing"})

            word_count = len(soup.get_text().split())
            results["word_count"].append({"url": page_url, "word_count": word_count})

            page_hash = hash(response.content)
            if page_hash in visited_pages:
                results["duplicate_pages"].append({"original": visited_pages[page_hash], "duplicate": page_url})
            else:
                visited_pages[page_hash] = page_url  # Store the URL with the hash

            h1_tags = soup.find_all('h1')
            if not h1_tags:
                results["h1_tags"].append(f"Missing H1 tag on URL: {page_url}")
            if len(h1_tags) > 1:
                results["h1_tags"].append(f"Multiple H1 tags on URL: {page_url}")

            h2_tags = soup.find_all('h2')
            if not h2_tags:
                results["h2_tags"].append(f"Missing H2 tag on URL: {page_url}")
            if len(h2_tags) > 1:
                results["h2_tags"].append(f"Multiple H2 tags on URL: {page_url}")

            meta_robots = soup.find('meta', attrs={'name': 'robots'})
            robots_content = meta_robots['content'] if meta_robots and 'content' in meta_robots.attrs else None
            if robots_content:
                results["meta_robots"].append({page_url: robots_content})

            meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
            refresh_content = meta_refresh['content'] if meta_refresh and 'content' in meta_refresh.attrs else None
            if refresh_content:
                results["meta_refresh"].append({"url": page_url, "content": refresh_content})

            canonical_link = soup.find('link', rel='canonical')
            canonical_href = canonical_link['href'] if canonical_link and 'href' in canonical_link.attrs else None
            if canonical_href:
                results["canonicals"].append({page_url: canonical_href})

            x_robots_tag = response.headers.get('X-Robots-Tag')
            if x_robots_tag:
                results["x_robots_tag"].append({page_url: x_robots_tag})

            next_link = soup.find('link', rel='next')
            prev_link = soup.find('link', rel='prev')
            if next_link and 'href' in next_link.attrs:
                results["pagination"].append({"url": page_url, "next": next_link['href']})
            if prev_link and 'href' in prev_link.attrs:
                results["pagination"].append({"url": page_url, "prev": prev_link['href']})

            for a in soup.find_all('a', href=True):
                if 'nofollow' in a.get('rel', []):
                    results["nofollow_links"].append({'url': a['href'], 'source_page': page_url})
                else:
                    results["follow_links"].append({'url': a['href'], 'source_page': page_url})

            redirect_chain = response.history
            if redirect_chain:
                chain = [{"url": r.url, "status_code": r.status_code} for r in redirect_chain]
                chain.append({"url": response.url, "status_code": response.status_code})
                results["redirect_chains"].append(chain)

            hreflangs = soup.find_all('link', rel='alternate', hreflang=True)
            for hreflang in hreflangs:
                results["hreflang_attributes"].append({
                    "url": page_url, 
                    "hreflang": hreflang['hreflang'], 
                    "href": hreflang['href']
                })

            amphtml = soup.find('link', rel='amphtml')
            if amphtml and 'href' in amphtml.attrs:
                results["amp_pages"].append({"url": page_url, "amphtml": amphtml['href']})

            breadcrumbs = soup.find_all('nav', attrs={'aria-label': 'breadcrumb'})
            for breadcrumb in breadcrumbs:
                results["breadcrumbs"].append({"url": page_url, "breadcrumb": breadcrumb.get_text().strip()})

        crawl_page(url)

        return JsonResponse(results)

    return JsonResponse({"errors": ["Invalid request method"]}, status=400)





# View function









    # issues

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_internal_issues(base_url, url, visited_urls):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        internal_links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/'):
                href = base_url + href
            if href.startswith(base_url) and href not in visited_urls:
                internal_links.add(href)
                
        return internal_links
    except Exception:
        return []

def check_link_status(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code
    except requests.exceptions.RequestException:
        return 'No Response'

def identify_issues(status_code):
    issues = []
    if status_code == 404:
        issues.append("Broken link (404 Not Found)")
    elif status_code >= 400 and status_code < 500:
        issues.append(f"Client error ({status_code})")
    elif status_code >= 500:
        issues.append(f"Server error ({status_code})")
    elif status_code == 'No Response':
        issues.append("No response from the server")
    return issues

def fix_issues(issues):
    fixes = []
    for issue in issues:
        if "Broken link" in issue:
            fixes.append("Check the URL for typos or update the link to a valid URL.")
        elif "Client error" in issue:
            fixes.append("Check the request and ensure it conforms to the server requirements.")
        elif "Server error" in issue:
            fixes.append("Investigate server issues and ensure the server is properly configured and running.")
        elif "No response" in issue:
            fixes.append("Ensure the server is running and accessible.")
    return fixes

def crawl_internal_links_issues(request):
    base_url = request.GET.get('base_url')
    max_pages = int(request.GET.get('max_pages', 50))  # Limit the number of pages to crawl
    if not base_url:
        return JsonResponse({'error': 'base_url parameter is required'}, status=400)
    
    visited_urls = set()
    to_visit_urls = [base_url]
    internal_links_status = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_link_status, url): url for url in to_visit_urls}

        while future_to_url and len(visited_urls) < max_pages:
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                status_code = future.result()
                visited_urls.add(url)
                
                issues = identify_issues(status_code)
                fixes = fix_issues(issues)
                internal_links_status.append({
                    'url': url,
                    'status_code': status_code,
                    'issues': issues,
                    'fixes': fixes
                })

                # Get internal links of the current URL
                internal_links = get_internal_issues(base_url, url, visited_urls)
                
                for link in internal_links:
                    if link not in visited_urls and len(visited_urls) < max_pages:
                        future_to_url[executor.submit(check_link_status, link)] = link

                if len(visited_urls) >= max_pages:
                    break

            future_to_url = {executor.submit(check_link_status, url): url for url in to_visit_urls if url not in visited_urls and url not in future_to_url}

    return JsonResponse({'internal_links_status': internal_links_status})




import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

def get_internal_links(base_url, url, visited_urls):
    """
    Extract internal links from a given URL.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        internal_links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)  # Resolve relative URLs
            if urlparse(full_url).netloc == urlparse(base_url).netloc and full_url not in visited_urls:
                internal_links.add(full_url)
                
        return internal_links
    except Exception:
        return []

def check_link_status(url):
    """
    Check the status code of a given URL.
    """
    try:
        response = requests.get(url, timeout=10)
        return response.status_code
    except requests.exceptions.RequestException:
        return 'No Response'

def identify_issues(status_code):
    """
    Identify issues based on the HTTP status code.
    """
    issues = []
    if status_code == 404:
        issues.append("Broken link (404 Not Found)")
    elif status_code >= 400 and status_code < 500:
        issues.append(f"Client error ({status_code})")
    elif status_code >= 500:
        issues.append(f"Server error ({status_code})")
    elif status_code == 'No Response':
        issues.append("No response from the server")
    return issues

def fix_issues(issues):
    """
    Provide recommendations for fixing identified issues.
    """
    fixes = []
    for issue in issues:
        if "Broken link" in issue:
            fixes.append("Check the URL for typos or update the link to a valid URL.")
        elif "Client error" in issue:
            fixes.append("Check the request and ensure it conforms to the server requirements.")
        elif "Server error" in issue:
            fixes.append("Investigate server issues and ensure the server is properly configured and running.")
        elif "No response" in issue:
            fixes.append("Ensure the server is running and accessible.")
    return fixes

def crawl_internal_links_issues(request):
    """
    Crawl all internal links of a given base URL and check their status.
    """
    base_url = request.GET.get('base_url')
    max_pages = int(request.GET.get('max_pages', 50))  # Limit the number of pages to crawl
    if not base_url:
        return JsonResponse({'error': 'base_url parameter is required'}, status=400)
    
    visited_urls = set()
    to_visit_urls = [base_url]
    internal_links_status = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        while to_visit_urls and len(visited_urls) < max_pages:
            future_to_url = {executor.submit(check_link_status, url): url for url in to_visit_urls}
            to_visit_urls = []  # Clear the list of URLs to visit next

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                status_code = future.result()
                visited_urls.add(url)
                
                issues = identify_issues(status_code)
                fixes = fix_issues(issues)
                internal_links_status.append({
                    'url': url,
                    'status_code': status_code,
                    'issues': issues,
                    'fixes': fixes
                })

                # Get internal links of the current URL
                internal_links = get_internal_links(base_url, url, visited_urls)
                
                for link in internal_links:
                    if link not in visited_urls and len(visited_urls) < max_pages:
                        to_visit_urls.append(link)

    return JsonResponse({'internal_links_status': internal_links_status})




# # allissues


# import asyncio
# import aiohttp
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from collections import deque
# from django.http import JsonResponse
# from django.views.decorators.http import require_GET

# # Analysis functions with consistent signature
# def analyze_indexability(soup, headers, url):
#     issues = []
#     if 'X-Robots-Tag' in headers and 'noindex' in headers['X-Robots-Tag'].lower():
#         issues.append('X-Robots-Tag header contains "noindex".')
#     if soup.find('meta', {'name': 'robots', 'content': 'noindex'}):
#         issues.append('Meta robots tag contains "noindex".')
#     return issues, 'Ensure pages that should be indexed do not have "noindex" directives.'

# def analyze_crawlability(soup, headers, url):
#     issues = []
#     if soup.find('meta', {'name': 'robots', 'content': 'nofollow'}):
#         issues.append('Meta robots tag contains "nofollow".')
#     return issues, 'Ensure pages that should be crawled do not have "nofollow" directives.'

# def analyze_redirects(soup, headers, url):
#     issues = []
#     try:
#         response = requests.get(url, allow_redirects=False)
#         if 300 <= response.status_code < 400:
#             issues.append(f'Redirect detected: {response.status_code} Location: {response.headers.get("Location")}')
#     except requests.RequestException as e:
#         issues.append(f'Error checking redirects: {str(e)}')
#     return issues, 'Avoid unnecessary redirects.'

# def analyze_https(soup, headers, url):
#     issues = []
#     if not url.startswith('https://'):
#         issues.append('URL does not use HTTPS.')
#     return issues, 'Ensure the site uses HTTPS.'

# def analyze_canonicalization(soup, headers, url):
#     issues = []
#     canonical = soup.find('link', {'rel': 'canonical'})
#     if canonical and canonical['href'] != url:
#         issues.append(f'Canonical URL mismatch: {canonical["href"]}')
#     return issues, 'Ensure the canonical URL is correct.'

# def analyze_structured_data(soup, headers, url):
#     issues = []
#     structured_data = soup.find_all('script', {'type': 'application/ld+json'})
#     if not structured_data:
#         issues.append('No structured data found.')
#     return issues, 'Implement structured data using JSON-LD.'

# def analyze_mobile_optimization(soup, headers, url):
#     issues = []
#     viewport = soup.find('meta', {'name': 'viewport'})
#     if not viewport:
#         issues.append('Viewport meta tag missing.')
#     return issues, 'Ensure the viewport meta tag is present for mobile optimization.'

# def analyze_meta_tags(soup, headers, url):
#     issues = []
#     if not soup.find('meta', {'name': 'description'}):
#         issues.append('Meta description tag missing.')
#     return issues, 'Add a meta description tag.'

# def analyze_headings(soup, headers, url):
#     issues = []
#     if not soup.find('h1'):
#         issues.append('H1 heading missing.')
#     return issues, 'Ensure an H1 heading is present.'

# def analyze_content_quality(soup, headers, url):
#     issues = []
#     text_length = len(soup.get_text(strip=True))
#     if text_length < 300:
#         issues.append('Page content is too short.')
#     return issues, 'Ensure sufficient content on the page.'

# def analyze_images(soup, headers, url):
#     issues = []
#     images = soup.find_all('img')
#     for img in images:
#         if not img.get('alt'):
#             issues.append(f'Image with src "{img.get("src")}" is missing alt text.')
#     return issues, 'Ensure all images have alt text.'

# def analyze_navigation(soup, headers, url):
#     issues = []
#     nav_links = soup.find_all('a', href=True)
#     if not nav_links:
#         issues.append('No navigation links found.')
#     return issues, 'Ensure navigation links are present.'

# def analyze_page_layout(soup, headers, url):
#     issues = []
#     if not soup.find('header'):
#         issues.append('Header element missing.')
#     if not soup.find('footer'):
#         issues.append('Footer element missing.')
#     return issues, 'Ensure header and footer elements are present.'

# def analyze_user_interaction(soup, headers, url):
#     issues = []
#     if not soup.find('button') and not soup.find('a', {'role': 'button'}):
#         issues.append('No interactive elements like buttons found.')
#     return issues, 'Ensure interactive elements are present.'

# def analyze_page_speed(soup, headers, url):
#     issues = []
#     # Placeholder for page speed analysis
#     return issues, 'Optimize page speed.'

# def analyze_caching(soup, headers, url):
#     issues = []
#     try:
#         response = requests.get(url)
#         if 'Cache-Control' not in response.headers:
#             issues.append('Cache-Control header missing.')
#     except requests.RequestException as e:
#         issues.append(f'Error checking caching: {str(e)}')
#     return issues, 'Ensure Cache-Control headers are set.'

# def analyze_server_performance(soup, headers, url):
#     issues = []
#     # Placeholder for server performance analysis
#     return issues, 'Optimize server performance.'

# def analyze_vulnerabilities(soup, headers, url):
#     issues = []
#     # Placeholder for vulnerability analysis
#     return issues, 'Address any security vulnerabilities.'

# def analyze_link_issues(soup, headers, url):
#     issues = []
#     links = soup.find_all('a', href=True)
#     for link in links:
#         href = link['href']
#         full_url = urljoin(url, href)
#         try:
#             response = requests.get(full_url, timeout=5)
#             if response.status_code >= 400:
#                 issues.append(f'Broken link detected: {full_url} (Status: {response.status_code})')
#         except requests.RequestException as e:
#             issues.append(f'Error checking link {full_url}: {str(e)}')
#     return issues, 'Fix or remove broken links.'

# def analyze_accessibility(soup, headers, url):
#     issues = []
#     if not soup.find('main'):
#         issues.append('Main landmark missing.')
#     if not soup.find('nav'):
#         issues.append('Navigation landmark missing.')
#     if not soup.find('footer'):
#         issues.append('Footer landmark missing.')
#     return issues, 'Ensure presence of main, navigation, and footer landmarks for accessibility.'

# def analyze_privacy(soup, headers, url):
#     issues = []
#     privacy_policies = soup.find_all('a', href=True)
#     if not any('privacy' in link['href'].lower() for link in privacy_policies):
#         issues.append('Privacy policy link missing.')
#     return issues, 'Ensure a privacy policy link is present on the site.'

# def analyze_social_media(soup, headers, url):
#     issues = []
#     social_links = ['facebook.com', 'twitter.com', 'instagram.com']
#     links = [a['href'] for a in soup.find_all('a', href=True)]
#     for social_link in social_links:
#         if not any(social_link in link for link in links):
#             issues.append(f'{social_link} link missing.')
#     return issues, 'Ensure links to Facebook, Twitter, and Instagram are present.'

# def analyze_localization(soup, headers, url):
#     issues = []
#     lang_tag = soup.find('html', lang=True)
#     if not lang_tag:
#         issues.append('HTML lang attribute missing.')
#     return issues, 'Add an HTML lang attribute for localization.'

# def analyze_sitemap_usage(soup, headers, url):
#     issues = []
#     sitemap_url = urljoin(url, '/sitemap.xml')
#     try:
#         response = requests.get(sitemap_url)
#         if response.status_code != 200:
#             issues.append('sitemap.xml file is missing or inaccessible.')
#     except requests.RequestException as e:
#         issues.append(f'Error checking sitemap.xml: {str(e)}')
#     return issues, 'Ensure a sitemap.xml file is present and accessible.'

# def analyze_robots_txt(soup, headers, url):
#     issues = []
#     robots_url = urljoin(url, '/robots.txt')
#     try:
#         response = requests.get(robots_url)
#         if response.status_code != 200:
#             issues.append('robots.txt file is missing or inaccessible.')
#     except requests.RequestException as e:
#         issues.append(f'Error checking robots.txt: {str(e)}')
#     return issues, 'Ensure a robots.txt file is present and accessible.'

# def analyze_miscellaneous(soup, headers, url):
#     issues = []
#     # Implement additional miscellaneous checks if necessary
#     return issues, 'Add any additional checks relevant to your site.'

# analyses = [
#     analyze_indexability,
#     analyze_crawlability,
#     analyze_redirects,
#     analyze_https,
#     analyze_canonicalization,
#     analyze_structured_data,
#     analyze_mobile_optimization,
#     analyze_meta_tags,
#     analyze_headings,
#     analyze_content_quality,
#     analyze_images,
#     analyze_navigation,
#     analyze_page_layout,
#     analyze_user_interaction,
#     analyze_page_speed,
#     analyze_caching,
#     analyze_server_performance,
#     analyze_vulnerabilities,
#     analyze_link_issues,
#     analyze_accessibility,
#     analyze_privacy,
#     analyze_social_media,
#     analyze_localization,
#     analyze_sitemap_usage,
#     analyze_robots_txt,
#     analyze_miscellaneous,
# ]

# async def fetch(session, url):
#     try:
#         async with session.get(url) as response:
#             html = await response.text()
#             headers = response.headers
#             soup = BeautifulSoup(html, 'html.parser')
#             return soup, headers, url
#     except Exception as e:
#         return None, None, url

# async def analyze_url(session, url):
#     soup, headers, url = await fetch(session, url)
#     if not soup:
#         return url, {'Error': ['Failed to fetch URL.']}
#     results = {}
#     for analysis in analyses:
#         issues, recommendation = analysis(soup, headers, url)
#         results[analysis.__name__] = {

#             'issues': issues,
#             'recommendation': recommendation
#         }
#     return url, results

# @require_GET
# async def allissues(request):
#     url = request.GET.get('url')
#     if not url:
#         return JsonResponse({'error': 'URL parameter is missing'}, status=400)

#     async with aiohttp.ClientSession() as session:
#         urls_to_crawl = [url]  # Initialize with the main URL

#         # Limit depth and number of pages to crawl
#         max_depth = 10
#         max_pages = 500

#         crawled_urls = set()
#         to_crawl = deque([(url, 0)])  # (url, depth)

#         while to_crawl and len(crawled_urls) < max_pages:
#             current_url, depth = to_crawl.popleft()
#             if depth > max_depth or current_url in crawled_urls:
#                 continue

#             crawled_urls.add(current_url)
#             soup, headers, url = await fetch(session, current_url)
#             if not soup:
#                 continue

#             links = [urljoin(current_url, a['href']) for a in soup.find_all('a', href=True)]
#             for link in links:
#                 if link not in crawled_urls and urlparse(link).netloc == urlparse(url).netloc:
#                     to_crawl.append((link, depth + 1))

#         tasks = [analyze_url(session, url) for url in crawled_urls]
#         results = await asyncio.gather(*tasks)

#         return JsonResponse(dict(results), status=200)
    

def check_image_optimization(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Ensure URL starts with http:// or https://
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            # Crawl the website to find all image URLs
            image_urls = crawl_website(url)

            results = []
            
            for img_url in image_urls:
                try:
                    # Fetch the image
                    img_response = requests.get(img_url)
                    img_response.raise_for_status()
                    
                    # Check image dimensions
                    image = Image.open(BytesIO(img_response.content))
                    width, height = image.size
                    
                    # Check file size (in KB)
                    file_size = len(img_response.content) / 1024

                    # Determine if dimensions and file size are optimized
                    dimensions_optimized = (width <= 1920 and height <= 1080)
                    file_size_optimized = (file_size <= 200)  # Example threshold

                    results.append({
                        'src': img_url,
                        'width': width,
                        'height': height,
                        'file_size_kb': round(file_size, 2),
                        'dimensions_optimized': dimensions_optimized,
                        'file_size_optimized': file_size_optimized
                    })

                except Exception as e:
                    results.append({
                        'src': img_url,
                        'error': str(e)
                    })

            return JsonResponse({'images': results})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    



    import requests
from django.http import JsonResponse
from bs4 import BeautifulSoup
from textstat import textstat
import spacy
from collections import Counter
from urllib.parse import urljoin, urlparse
from collections import deque

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join(p.get_text() for p in paragraphs)
    return text

def extract_headings_text(soup):
    headings_text = ' '.join([heading.get_text() for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
    return headings_text

def analyze_content_quality(text, headings_text):
    # Calculate readability scores
    readability_scores = {
        'flesch_reading_ease': textstat.flesch_reading_ease(text),
        'smog_index': textstat.smog_index(text),
        'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
        'coleman_liau_index': textstat.coleman_liau_index(text),
        'automated_readability_index': textstat.automated_readability_index(text),
        'dale_chall_readability_score': textstat.dale_chall_readability_score(text),
        'difficult_words': textstat.difficult_words(text),
        'linsear_write_formula': textstat.linsear_write_formula(text),
        'gunning_fog': textstat.gunning_fog(text),
    }

    # Extract keywords using spaCy
    doc = nlp(text)
    nouns = [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    
    # Extract keywords from headings
    heading_doc = nlp(headings_text)
    heading_nouns = [token.text.lower() for token in heading_doc if token.pos_ in ['NOUN', 'PROPN']]

    # Count the frequency of each noun in the text and headings
    noun_freq = Counter(nouns)
    heading_noun_freq = Counter(heading_nouns)

    # Determine primary keyword as the most frequent noun in headings
    primary_keyword = heading_noun_freq.most_common(1)[0][0] if heading_noun_freq else None

    return {
        'readability_scores': readability_scores,
        'primary_keyword': primary_keyword,
        'top_keywords': noun_freq.most_common(10)
    }

def crawl_website(start_url, max_depth=2):
    visited = set()
    queue = deque([(start_url, 0)])
    results = {}

    while queue:
        current_url, depth = queue.popleft()
        if depth > max_depth:
            continue
        
        if current_url in visited:
            continue

        visited.add(current_url)
        
        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract page title
                title = soup.title.get_text() if soup.title else 'No Title'
                
                # Extract content and headings
                content = extract_text_from_html(response.text)
                headings_text = extract_headings_text(soup)
                
                # Analyze content quality
                analysis_result = analyze_content_quality(content, headings_text)
                
                # Store results with page title
                results[title] = analysis_result

                # Find all links to crawl further
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    full_url = urljoin(current_url, href)
                    
                    # Avoid re-crawling and ensure we only follow links within the same domain
                    if urlparse(full_url).netloc == urlparse(start_url).netloc:
                        queue.append((full_url, depth + 1))
                        
        except requests.RequestException as e:
            print(f"Error fetching {current_url}: {e}")

    return results

def content_quality_analysis(request):
    if request.method == 'GET':
        url = request.GET.get('url')

        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)

        try:
            # Ensure URL starts with http:// or https://
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url

            # Crawl the website to get content and headings
            results = crawl_website(url)

            return JsonResponse(results)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)
    





    # views.py

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
from textblob import TextBlob
import requests

def get_internal_links(base_url, url, visited_urls):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        internal_links = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/'):
                href = base_url + href
            if href.startswith(base_url) and href not in visited_urls:
                internal_links.add(href)

        return internal_links
    except Exception as e:
        return []

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def crawl_website(base_url):
    visited_urls = set()
    to_visit_urls = [base_url]
    content_sentiment = []

    while to_visit_urls:
        current_url = to_visit_urls.pop(0)
        visited_urls.add(current_url)

        try:
            response = requests.get(current_url)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            polarity, subjectivity = analyze_sentiment(text)
            content_sentiment.append({
                'url': current_url,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'text': text[:200]  # Truncate text for preview
            })

            internal_links = get_internal_links(base_url, current_url, visited_urls)
            for link in internal_links:
                if link not in visited_urls and link not in to_visit_urls:
                    to_visit_urls.append(link)

        except Exception as e:
            continue

    return content_sentiment

def analyze_website_sentiment(request):
    base_url = request.GET.get('base_url')
    if not base_url:
        return JsonResponse({'error': 'base_url parameter is required'}, status=400)

    content_sentiment = crawl_website(base_url)
    return JsonResponse({'content_sentiment': content_sentiment})

# analyze_seoinfo

import logging
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Set up logging
logger = logging.getLogger(__name__)
MAX_PAGES = 100  # Define your max pages limit here

@require_http_methods(["GET"])
def analyze_seoinfo(request):
    url = request.GET.get('url')
    if not url:
        return JsonResponse({'error': 'URL parameter is missing'}, status=400)

    try:
        pages_to_crawl = {url}
        crawled_pages = {}
        visited_pages = set()

        while pages_to_crawl and len(crawled_pages) < MAX_PAGES:
            page = pages_to_crawl.pop()
            if page in visited_pages:
                continue
            visited_pages.add(page)

            result = get_page_links(page)  # Assuming this function is defined elsewhere
            title, canonical_url, links = result

            if title != 'Error fetching page':
                crawled_pages[page] = {'title': title, 'canonical_url': canonical_url, 'links': links}
                pages_to_crawl.update(links - visited_pages)

        analysis_results = []
        for page, data in crawled_pages.items():
            title = data['title']
            links = data['links']
            canonical_url = data.get('canonical_url', '')

            # 1) Page has links to broken pages
            broken_links = [link for link in links if is_broken_link(link)]  # Assuming this function is defined

            # 2) Page has no outgoing links
            no_outgoing_links = not bool(links)

            # 3) Canonical URL has no incoming internal links
            incoming_links = [link for link, link_data in crawled_pages.items() if canonical_url in link_data['links']]
            no_incoming_links = not incoming_links

            # 4) HTTPS page has internal links to HTTP
            internal_http_links = [
                link for link in links 
                if link.startswith('http://') and urlparse(link).netloc == urlparse(page).netloc
            ]

            # 5) Meta description length and presence
            try:
                response = requests.get(page)
                soup = BeautifulSoup(response.text, 'html.parser')
                meta_description_tag = soup.find('meta', attrs={'name': 'description'})
                meta_description = meta_description_tag['content'] if meta_description_tag and 'content' in meta_description_tag.attrs else 'No meta description'
                meta_description_length = len(meta_description)
            except Exception as e:
                logger.error(f"Error fetching or parsing meta description for {page}: {str(e)}")
                meta_description = 'Error retrieving meta description'
                meta_description_length = 0

            analysis_results.append({
                'page': page,
                'title': title,
                'broken_links': broken_links,
                'no_outgoing_links': no_outgoing_links,
                'incoming_links_to_canonical': incoming_links,
                'internal_http_links_on_https_page': internal_http_links,
                'meta_description': meta_description,
                'meta_description_length': meta_description_length,
                'has_meta_description': meta_description_length > 0
            })

        return JsonResponse(analysis_results, safe=False, status=200)

    except Exception as e:
        logger.error(f"Error in analyze_seoinfo: {str(e)}", exc_info=True)
        return JsonResponse({'message': 'An error occurred while trying to analyze the webpage', 'error': str(e)}, status=500)

