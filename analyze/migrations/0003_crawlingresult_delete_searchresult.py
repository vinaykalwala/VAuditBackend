# Generated by Django 5.0.2 on 2024-09-13 11:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyze', '0002_userwebsite'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlingResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('internal_links_count', models.IntegerField()),
                ('external_links_count', models.IntegerField()),
                ('backlinks_count', models.IntegerField()),
                ('dofollow_links_count', models.IntegerField()),
                ('nofollow_links_count', models.IntegerField()),
                ('canonical_urls_count', models.IntegerField()),
                ('non_canonical_urls_count', models.IntegerField()),
                ('crawled_links_count', models.IntegerField()),
                ('uncrawled_links_count', models.IntegerField()),
                ('image_count', models.IntegerField()),
                ('broken_images_count', models.IntegerField()),
                ('title_info_count', models.IntegerField()),
                ('h1_info_count', models.IntegerField()),
                ('meta_description_info_count', models.IntegerField()),
                ('broken_links_count', models.IntegerField()),
                ('word_count_info_count', models.IntegerField()),
                ('non_html_files_count', models.IntegerField()),
                ('html_pages_count', models.IntegerField()),
                ('indexed_urls_count', models.IntegerField()),
                ('non_indexed_urls_count', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='SearchResult',
        ),
    ]
