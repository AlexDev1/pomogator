import pymorphy2
from django.db import models

from core.mixins import CountVisitMixin, VisitsMixin

morph = pymorphy2.MorphAnalyzer()


class Country(CountVisitMixin, VisitsMixin, models.Model):
    title = models.CharField(
        max_length=50, verbose_name=u'страна', db_index=True)
    code = models.CharField(max_length=3)
    slug = models.CharField(max_length=50, db_index=True)
    lang = models.CharField(max_length=250, verbose_name=u'язык', blank=True)
    last_update_news = models.DateTimeField('Изменено', blank=True, null=True)

    class Meta:
        verbose_name = u"Страна"
        verbose_name_plural = u"Страны"
        ordering = ('title',)
        app_label = 'countries'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news:news-by-country', args=(self.slug,))

    @property
    def title_rod(self):
        p = morph.parse(self.title)[0]
        rod_title = p.inflect({'gent'})
        if rod_title:
            return rod_title.word.title()
        else:
            return self.title
