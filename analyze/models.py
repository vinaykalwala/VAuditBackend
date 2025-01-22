from django.db import models
from django.contrib.auth import get_user_model
from django.forms import JSONField
from django.conf import settings

from django.db import models
from django.conf import settings

class CrawlingResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.URLField()
    
    # Store the actual internal links and their count
    internal_links = models.JSONField(default=list)  # Store internal links as a list
    internal_links_count = models.IntegerField(default=0)  # Store the count of internal links

    external_links = models.JSONField(default=list)  # Storing external links as a list
    backlinks = models.JSONField(default=list)  # Storing backlinks as a list
    dofollow_links = models.JSONField(default=list)  # Storing dofollow links as a list
    nofollow_links = models.JSONField(default=list)  # Storing nofollow links as a list
    canonical_urls = models.JSONField(default=list)  # Storing canonical URLs
    non_canonical_urls = models.JSONField(default=list)  # Storing non-canonical URLs

    # Other fields for counts
    external_links_count = models.IntegerField(default=0)
    backlinks_count = models.IntegerField(default=0)
    dofollow_links_count = models.IntegerField(default=0)
    nofollow_links_count = models.IntegerField(default=0)
    canonical_urls_count = models.IntegerField(default=0)
    non_canonical_urls_count = models.IntegerField(default=0)
    crawled_links_count = models.IntegerField(default=0)
    uncrawled_links_count = models.IntegerField(default=0)
    image_count = models.IntegerField(default=0)
    broken_images_count = models.IntegerField(default=0)
    title_info_count = models.IntegerField(default=0)
    h1_info_count = models.IntegerField(default=0)
    meta_description_info_count = models.IntegerField(default=0)
    broken_links_count = models.IntegerField(default=0)
    word_count_info_count = models.IntegerField(default=0)
    non_html_files_count = models.IntegerField(default=0)
    html_pages_count = models.IntegerField(default=0)
    indexed_urls_count = models.IntegerField(default=0)
    non_indexed_urls_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'url')

    def __str__(self):
        return f"{self.user} - {self.url}"






from django.db import models
from django.conf import settings  # Import settings to use AUTH_USER_MODEL
import json

class UserWebsite(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='website_data')
    urls = models.TextField(default='[]')  # Store URLs as a JSON-encoded list

    def add_url(self, url):
        current_urls = json.loads(self.urls)
        if url not in current_urls:
            current_urls.append(url)
            self.urls = json.dumps(current_urls)
            self.save()

    def get_urls(self):
        return json.loads(self.urls)
