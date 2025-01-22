from django.urls import path
from . import views 
from .views import *
from analyze.views import *
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts .views import *



urlpatterns = [
   path('images/', views.images, name='images'),
   path("errorlinks/",views.errorlinks),
   
  
   path("urls/",url,name="urls"),
   path("sitemaps/",extract_sitemaps, name="sitemap"),
   path("social/",socialtags, name="socialtags"),
   path("status/",find_links_with_status_200),
   path("webstatus/", find_links_with_status_200_in_website, name="webstatus"),
   path("analyse/",analyze_website),
   path("imagesone/",imagesone),




    # todays
    path("full-content-links/", overview,name='overview'),
    path("countsitemaps/",views.count_sitemaps,name='countsitemaps'),
    path("analyze_canonical_urls/",views.analyze_canonical_urls,name='analyze_canonical_urls'),
    path("analyze_content/",analyze_content),
    path("analyze_resources/",analyze_resources,name='analyze_resources'),
    path("analyze_links/",analyze_links),
    # path("analyze_indexability/",analyze_indexability),
    path("analyze_social_tags/",analyze_social_tags_info),
    # path("spanscore/",calculate_spam_score),
    path("find_duplicate_content/",find_duplicate_content),
    path("keyword_suggestion/",keyword_suggestion),
    path("site_audit/",site_audit),
    path("analyze_optimization/",analyze_optimization),
    path('get_title/',get_title),
    path('api/internal-links/',get_internal_linksonly , name='get_internal_links' ),
    path('internalissues/', crawl_internal_links_issues, name='crawl_internal_links_issues'),

# 7/26
path('check-image-optimization/', check_image_optimization, name='check_image_optimization'),
path('content_quality_analysis/',content_quality_analysis),

path('competitor_analysis/', competitor_analysis, name='competitor_analysis'),
path("analyseinfo/", analyze_websiteinfo),

path('check_snippets/', check_snippets, name='check_snippets'),
path('page_loading_speed/', page_loading_speed, name='page_loading_speed'),
path('check-website-accessibility/', check_website, name='check_website_accessibility'),
path('analyze-seo/', analyze_seoinfo, name='analyze_seo'),
path('analyze-seotool/', analyze_seotool, name='analyze_seotool'),
path('seo_analysis/', seo_analysis, name='analyze_seotool'),
path('crawl_internal_links_issues/',crawl_internal_links_issues),
path('errorinfoissue/',errorinfoissue,  name='errorinfoissue'),
path('user-websites/', get_user_websites, name='user_websites'),
path('api/crawling-results/', CrawlingResultsView.as_view(), name='crawling-results-list'),
path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
path('api/get_crawling_results/', get_crawling_results, name='get_crawling_results'),

] 





