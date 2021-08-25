from django.apps import AppConfig
from watson import search as watson

class NewsConfig(AppConfig):
    name = 'news'
    verbose_name = '1. Новости и статьи'

    def ready(self):
        import news.signals  # noqa
        # Search for News
        News = self.get_model("News")
        watson.register(News)
        # Search for Article
        Article = self.get_model("Article")
        watson.register(Article)
