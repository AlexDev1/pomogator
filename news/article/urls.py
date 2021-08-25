from django.conf.urls import url

from .views import (
    ArticleListView,
    ArticleDetailView,
    RubricArticleListView,
)

app_name = 'articles'

urlpatterns = [
    # '',
    url(r'^$', ArticleListView.as_view(), name="list"),
    url(r'^(?P<pk>\d+)/$', ArticleDetailView.as_view(), name="detail"),
    url(r'^(?P<rubric_name>.*)/$', RubricArticleListView.as_view(), name='article_by_rubric'),
]
