from django.db.models import Q
from django.shortcuts import get_object_or_404
# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView

from core.mixins import VisitViewMixin
from countries.models import Country
from news.models import News, Rubric, Stories


class IndexPage(TemplateView):
    template_name = 'index.html'


class NewsList(ListView):
    model = News
    paginate_by = 20
    template_name = 'news/list.html'

    def get_queryset(self):
        qs = self.model.objects.filter(published=True)
        return qs


class NewsRubric(ListView):
    model = News
    paginate_by = 20
    template_name = 'news/list.html'
    rubric = None

    def get_queryset(self):
        rubric = get_object_or_404(Rubric, slug=self.kwargs.get('slug', None))
        # rubric = Rubric.objects.get(slug=self.kwargs.get('slug', None))
        self.rubric = rubric
        qs = self.model.objects.filter(published=True)
        qs = qs.filter(rubrics=rubric)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(NewsRubric, self).get_context_data(**kwargs)
        context['rubric'] = self.rubric
        return context


class NewsStories(ListView):
    model = News
    paginate_by = 20
    template_name = 'news/list_stories.html'
    rubric = None

    def get_queryset(self):
        rubric = get_object_or_404(Stories, slug=self.kwargs.get('slug', None))
        # rubric = Rubric.objects.get(slug=self.kwargs.get('slug', None))
        self.rubric = rubric
        qs = self.model.objects.filter(published=True)
        qs = qs.filter(stories=rubric)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(NewsStories, self).get_context_data(**kwargs)
        context['rubric'] = self.rubric
        return context


class NewsDetail(VisitViewMixin, DetailView):
    model = News
    template_name = 'news/detail.html'
    queryset = News.objects.all_objects().filter(Q(published=True) | Q(delayed_publication=True))


class CountryNewsListView(ListView):
    paginate_by = 20
    template_name = "news/list_country.html"

    def get_queryset(self, **kwargs):
        return News.objects.filter(
            published=True,
            countries__slug=self.kwargs.get('slug')
        )

    def get_context_data(self, **kwargs):
        context = super(CountryNewsListView, self).get_context_data(**kwargs)
        context['country'] = get_object_or_404(
            Country,
            slug=self.kwargs.get('slug')
        )
        return context
