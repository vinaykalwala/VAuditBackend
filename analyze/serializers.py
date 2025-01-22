# serializers.py
from rest_framework import serializers
from .models import CrawlingResult

class CrawlingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlingResult
        fields = [
            'id',
            'url',
            'internal_links',
            'internal_links_count',
            'external_links',
            'backlinks',
            'dofollow_links',
            'nofollow_links',
            'canonical_urls',
            'non_canonical_urls',
            'external_links_count',
            'backlinks_count',
            'dofollow_links_count',
            'nofollow_links_count',
            'canonical_urls_count',
            'non_canonical_urls_count',
            'crawled_links_count',
            'uncrawled_links_count',
            'image_count',
            'broken_images_count',
            'title_info_count',
            'h1_info_count',
            'meta_description_info_count',
            'broken_links_count',
            'word_count_info_count',
            'non_html_files_count',
            'html_pages_count',
            'indexed_urls_count',
            'non_indexed_urls_count',
            'created_at'
        ]
