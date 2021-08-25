from django.db import models

from countries.models import Country


class WidgetRegion(models.Model):
    """ над первой новостью, 2) между пятой и шестой, 3) между 10 и 11 новостью (как на Турпроме) """
    SECTIONS = (
        (0, 'Сквозной шапка'),
        (1, 'Сквозной под меню'),
        (2, 'В левой колонке над новостью'),
        (3, 'В левой колонке ПОД новостью'),
        (4, 'В правой колонке на страницах новостей, статей'),
        (5, 'Список новостей, над 1 новостью '),
        (6, 'Список новостей, между 5 и 6'),
        (7, 'Список новостей, между 10 и 11'),
        # (5, 'Внутри новости под текстом'),
        # (6, 'Внутри Туропедии'),
    )

    # all_countries = models.BooleanField("Все страны", help_text="Скрипты для тех стран у которых нет своих виджетов",
    #                                     default=False, db_index=True)
    # country = models.ForeignKey(Country, verbose_name='Страна', related_name='widgets', on_delete=models.CASCADE,
    #                             blank=True, null=True)
    section = models.PositiveSmallIntegerField('Видимость', choices=SECTIONS, unique=True,
                                               blank=False, null=False, default=0, db_index=True)
    title = models.CharField('Название', max_length=255, help_text="Название для блока виджета")
    active = models.BooleanField(verbose_name='Активный', default=False, db_index=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Виджет'
        verbose_name_plural = 'Виджеты'

    def __str__(self):
        return self.title

    def clean(self):
        if not self.get_widgets():
            self.active = False
            return super(WidgetRegion, self).save()
        else:
            return super(WidgetRegion, self).save()

    def get_widgets(self):
        return WidgetScript.objects.filter(region=self, active=True)


class WidgetScript(models.Model):
    """Скрипты виджетов и рекламных баннеров"""
    region = models.ForeignKey(WidgetRegion, on_delete=models.CASCADE)
    name = models.CharField('Название', max_length=255, default='', blank=False, null=False)
    content = models.TextField('HTML-код скрипта', max_length=5000, blank=True)
    active = models.BooleanField(verbose_name='Активный', default=False, db_index=True)
    order = models.PositiveSmallIntegerField("Сортировка", default=0, blank=False, null=False, db_index=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Скрипт виджета"
        verbose_name_plural = "Скрипты виджета"

    def __str__(self):
        return self.name
