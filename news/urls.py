
from django.urls import path, re_path

from .views import NewsList, NewsRubric, NewsDetail, NewsStories, CountryNewsListView

app_name = 'news'

urlpatterns = [
    path('', NewsList.as_view(), name='list'),
    re_path(r'^news-(?P<slug>.*)/$', CountryNewsListView.as_view(),name='news-by-country'),
    path('<int:pk>/', NewsDetail.as_view(), name='detail'),
    path('<slug:slug>/', NewsRubric.as_view(), name='rubric'),
    path('stories/<slug:slug>/', NewsStories.as_view(), name='stories'),
]
