from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import path, include, re_path
from django.views.decorators.cache import cache_page
from django.views.static import serve

from core.views import SearchResultsView, FeedbackView
from filebrowser.sites import site as filebrowser_site
from news.views import IndexPage
from pomogator import settings
from pomogator.feeds import show_feed
from pomogator.sitemap import StaticSitemap, DinamicNewsSitemap, DinamicArticleSitemap, DinamicPageSitemap, \
    DinamicRubricSitemap, DinamicCountrySitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'static': StaticSitemap,
    'rubrics': DinamicRubricSitemap,
    'news': DinamicNewsSitemap,
    'article': DinamicArticleSitemap,
    'page': DinamicPageSitemap,
    'country': DinamicCountrySitemap,
}

urlpatterns = [
    path('', IndexPage.as_view(), name='index'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('admin/filebrowser/', filebrowser_site.urls),
    path('trumbowyg/', include('trumbowyg.urls')),
    path('photologue/', include('photologue.urls', namespace='photologue')),
    path('news/', include('news.urls', namespace='news')),
    path('articles/', include('news.article.urls', namespace="articles")),
    path('feedback/', FeedbackView.as_view(), name="feedback"),
    # partners
    re_path(r'^', include('partners.urls')),
    #
    re_path(r'^robots\.txt', include('robots.urls')),
    # re_path(r'^sitemap.xml$', cache_page(60)(sitemap), {'sitemaps': [sitemaps]}, name='cached-sitemap'),
    re_path(r'^sitemap.xml$', sitemap, {'sitemaps': sitemaps}, name='cached-sitemap'),
    re_path(r'^feed/(?P<feed_name>.*)\.xml$', show_feed),
    re_path('media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
    re_path(r'^(?P<url>.*/)$', views.flatpage),

]
