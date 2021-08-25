from django.db import models
from tinymce import HTMLField

from news.models import Stories


class SEOFieldsMixin(models.Model):
    """ SEO абстрактная модель"""
    meta_title = models.CharField(u'Meta Title', max_length=255, blank=True)
    meta_description = models.TextField(u'Meta Description', blank=True)
    meta_keywords = models.TextField(u'Meta Keywords', blank=True)

    class Meta:
        abstract = True


class PartnerPage(SEOFieldsMixin):
    """
    Страницы партнеров с виджетами
    """

    title = models.CharField('Название', max_length=255)
    subtitle = models.CharField(verbose_name='Подзаголовок', max_length=200, blank=True, null=True)
    disc = HTMLField('HTML-Описание', max_length=5000, blank=True)
    slug = models.CharField('Slug', max_length=255, unique=True, help_text="Например tours-online, avia-online и тп")
    news_subjects = models.ManyToManyField(Stories, blank=True, verbose_name=u'Сюжеты', related_name='news_subjects')

    class Meta:
        verbose_name = 'Страница партнеров с виджетами'
        verbose_name_plural = 'Страницы партнеров с виджетами'

    def __str__(self):
        return self.title


class PartnerWidgetScript(models.Model):
    """
    Скрипты виджетов по а/б, турам и отелям
    """
    region = models.ForeignKey(PartnerPage,  on_delete=models.CASCADE)
    name = models.CharField('Название', max_length=255,  default='', blank=False, null=False)
    content = models.TextField('HTML-код скрипта', max_length=5000, blank=True)
    order = models.PositiveSmallIntegerField("Сортировка", default=0, blank=False, null=False)

    class Meta:
        ordering = ['order']
        verbose_name = "Скрипт виджета"
        verbose_name_plural = "Скрипты виджета"

    def __str__(self):
        return self.name
