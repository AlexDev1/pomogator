

import logging

# from django.http import Http404
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView

from core.mixins import VisitViewMixin
from ..models import Article, Rubric
from countries.models import Country

log = logging.getLogger(__name__)


class ArticleListView(ListView):
    paginate_by = 20
    template_name = "articles/article_list.html"
    model = Article
    current_country = None
    current_tourismtype = None

    def get(self, request, *args, **kwargs):
        return super(ArticleListView, self).get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        # print(self.request.GET.get('tourismtype'))

        qs = self.model.objects.filter(
            published=True, pubdate__lte=timezone.now())

        if 'country' in self.request.GET:
            country_slug = self.request.GET.get('country')
            self.current_country = get_object_or_404(
                Country, slug=country_slug)
            qs = qs.filter(countries=self.current_country)

        return qs

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        context['h1'] = "Журнал: статьи по туризму"
        context['show_map'] = True
        context['current_country'] = self.current_country
        context['current_tourismtype'] = self.current_tourismtype
        return context


class ArticleDetailView(VisitViewMixin, DetailView):
    template_name = "articles/article_detail.html"
    model = Article
    queryset = Article.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        same_articles = Article.objects.filter(
            published=True
        ).exclude(id=self.object.id).order_by("-created")

        if same_articles.count():
            context['same_articles'] = same_articles[0]

        return context


class RubricArticleListView(ListView):
    paginate_by = 20
    model = Article
    template_name = "articles/article_list.html"
    rubric = None
    current_country = None
    current_tourismtype = None

    def get(self, request, *args, **kwargs):
        self.rubric = get_object_or_404(Rubric, title_en=kwargs['rubric_name'])
        return super(RubricArticleListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(published=True, rubrics=self.rubric)

    def get_context_data(self, **kwargs):
        context = super(RubricArticleListView, self).get_context_data(**kwargs)
        context['h1'] = self.rubric.title
        context['show_map'] = False
        context['current_country'] = self.current_country
        context['rubric'] = self.rubric
        return context
