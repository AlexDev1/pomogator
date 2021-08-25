from django.contrib.flatpages.models import FlatPage
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.requests import RequestSite
from django.urls import reverse
from robots.models import Rule
from robots.views import RuleList

from countries.models import Country
from news.models import News, Article, Rubric


class SiteEduRuleList(RuleList):

    def get_current_site(self, request):
        return RequestSite(request)

    def get_queryset(self):
        return Rule.objects.filter(sites=1)

    def get_context_data(self, **kwargs):
        context = super(RuleList, self).get_context_data(**kwargs)
        context['sitemap_urls'] = self.get_sitemap_urls()
        context['host'] = 'http://%s' % self.current_site.domain
        return context


rules_list = SiteEduRuleList.as_view()


class StaticSitemap(Sitemap):
    """For static"""
    changefreq = "weekly"
    priority = 0.5
    domain = ''

    def items(self):
        return [
            'index',
            'news:list',
            'articles:list'

        ]

    def location(self, object):
        return reverse(object)


class DinamicNewsSitemap(Sitemap):
    """For News"""
    changefreq = "daily"
    priority = 0.5
    domain = ''

    def items(self):
        return News.objects.filter(published=True)

    def lastmod(self, News):
        return News.pubdate

    def location(self, News):
        return News.get_absolute_url()


class DinamicArticleSitemap(Sitemap):
    """For Article"""
    changefreq = "daily"
    priority = 0.5
    domain = ''

    def items(self):
        return Article.objects.filter(published=True)

    def lastmod(self, Article):
        return Article.pubdate

    def location(self, Article):
        return Article.get_absolute_url()


class DinamicPageSitemap(Sitemap):
    """For Page"""
    changefreq = "daily"
    priority = 0.5
    domain = ''

    def items(self):
        return FlatPage.objects.all()

    # def lastmod(self, FlatPage):
    #     return Article.pubdate

    def location(self, Article):
        return Article.get_absolute_url()


class DinamicCountrySitemap(Sitemap):
    """For Country"""
    changefreq = "daily"
    priority = 0.5
    domain = ''

    def items(self):
        return Country.objects.all()

    def lastmod(self, Country):
        return Country.last_update_news

    def location(self, Country):
        return Country.get_absolute_url()


class DinamicRubricSitemap(Sitemap):
    """For Rubric"""
    changefreq = "daily"
    priority = 0.5
    domain = ''

    def items(self):
        return Rubric.objects.all()

    def lastmod(self, Rubric):
        return Rubric.last_update

    def location(self, Rubric):
        return Rubric.get_absolute_url()
