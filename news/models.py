import os
from datetime import datetime
from itertools import chain

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.db.models import signals
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from mptt.managers import TreeManager
from photologue.models import ImageModel
from pytils.translit import translify
from tinymce import HTMLField

from comments.models import Comment
from core.fields import YoutubeVideoLinkMixin
from core.html_cleanup import seo_clean_content
from core.mixins import CountVisitMixin, FakeVisitMixin, TimeStampMixin
from core.utils import clean_word, sanitize_html, resize_image, sanitize_html_comment
from countries.models import Country


class Author(models.Model):
    full_name = models.CharField('Имя и фамилия', max_length=150)
    active = models.BooleanField('Активный')

    def __str__(self):
        return '%s' % self.full_name

    class Meta:
        verbose_name = "Автор новости"
        verbose_name_plural = "Авторы новостей"


class Source(models.Model):
    name = models.CharField('Название', max_length=150)
    url = models.CharField('URL', max_length=150)

    def __str__(self):
        return '<a href={}>{}</a>'.format(self.url, self.name)

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"


class Rubric(models.Model):
    order = models.PositiveSmallIntegerField("Сортировка", default=0, blank=False, null=False)
    title = models.CharField(verbose_name="Название", max_length=50)
    title_en = models.CharField(verbose_name="Название (англ.)", max_length=50,
                                db_index=True)
    text = models.TextField(verbose_name="Описание")
    slug = models.SlugField(max_length=50, db_index=True)
    last_update = models.DateTimeField('Изменено', blank=True, null=True)

    def __str__(self):
        return self.title

    def count_news(self):
        count = cache.get('rubric_%d_count_news' % self.id)
        if not count:
            count = News.objects.filter(rubrics=self.id).count()
            cache.set('rubric_%d_count_news' % self.id, count, 3 * 60 * 60)
        return count

    def get_absolute_url(self):
        return reverse('news:rubric', args=[self.slug, ])

    class Meta:
        ordering = ['order']
        verbose_name = "Рубрика новости"
        verbose_name_plural = "Рубрики новостей"


class Stories(models.Model):
    """Сюжеты"""
    title = models.CharField('Название', max_length=150)
    active = models.BooleanField('Актуальный')
    slug = models.SlugField(max_length=150, null=True, blank=True)
    image = models.ImageField(verbose_name='Картинка', blank=True, null=True)
    description = models.TextField('Описание', blank=True, null=True)
    order = models.PositiveSmallIntegerField(verbose_name='Order', default=0,
                                             null=False, db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:stories', args=[self.slug])

    def top_news(self):
        return self.news.filter(published=True).all()[:5]

    def count_new(self):
        return self.stories.count()

    class Meta:
        ordering = ['order']
        verbose_name = "Сюжет новости"
        verbose_name_plural = "Сюжеты новостей"


class SpecialBlock(models.Model):
    """Спецблоки для новстей"""
    name = models.CharField('Название', max_length=150)
    lastnews_date = models.DateTimeField(
        verbose_name='Дата последней новости',
        null=True,
        blank=True
    )

    def __str__(self):
        return '%s' % self.name

    class Meta:
        verbose_name = "Специальный блок новостей"
        verbose_name_plural = "Специальные блоки новостей"
        ordering = ("-lastnews_date",)

    def save(self):
        if self.id:
            news = self.news.all()[:1]
            article = self.articles.all()[:1]
            if len(news) > 0:
                self.lastnews_date = news[0].pubdate
            if len(article) > 0:
                if self.lastnews_date < article[0].pubdate:
                    self.lastnews_date = article[0].pubdate
        super(SpecialBlock, self).save()

    def get_latest_news(self):
        news = self.news.filter(published=True)[:3]
        articles = self.articles.filter(published=True)[:3]
        result_list = list(
            sorted(
                chain(news, articles),
                key=lambda instance: instance.get_date_for_sorted(),
                reverse=True)
        )
        return result_list

    def get_latest_articles(self):
        return self.articles.filter(published=True)[:3]


class PublishManager(models.Manager):

    def all_objects(self):
        """Для Админки чтобы видно было все записи"""
        return super().get_queryset().all()

    def get_queryset(self):
        """Только опубликованные для всех запросов которые используют News.objects.filter(**)"""
        from django.utils import timezone
        today = timezone.now()
        return super().get_queryset().filter(published=True, pubdate__lte=today)

    def unpublished_count(self):
        return super().get_queryset().filter(published=False).count()

    def publish(self):
        # from datetime import datetime
        today = datetime.now()
        return self.get_queryset().filter(published=True, pubdate__lte=today)


class News(CountVisitMixin, FakeVisitMixin, YoutubeVideoLinkMixin, models.Model):
    FAKE_VISITS_RANGE = (0, 6)

    video_link_field_name = 'youtube_video'

    title = models.CharField('Заголовок', max_length=200)
    subtitle = models.CharField('Подзаголовок', max_length=200, blank=True, null=True)
    pubdate = models.DateTimeField('Дата публикации', db_index=True)
    delayed_publication = models.BooleanField("Отложенная публикация", default=False, db_index=True)
    text = HTMLField('Тескт')
    authors = models.ManyToManyField(Author, verbose_name='Авторы', blank=True)
    # source = models.ForeignKey(Source, verbose_name=u'Источник', blank=True, null=True,
    #                            on_delete=models.SET_NULL)
    # slug = models.SlugField("URL", max_length=200)
    countries = models.ManyToManyField(Country,
                                       verbose_name=u'Страны')
    rubrics = models.ManyToManyField(Rubric, verbose_name='Рубрики для новости',
                                     related_name='rubrics')
    stories = models.ManyToManyField(Stories, blank=True, verbose_name='Сюжеты',
                                     related_name='stories')

    published = models.BooleanField(verbose_name=u'Опубликовано', default=False,
                                    db_index=True)
    rss_exclude = models.BooleanField(u'Исключить из RSS', default=False)

    youtube_video = models.URLField(verbose_name=u"Ссылка на видео", max_length=1024,
                                    blank=True,
                                    help_text=u"Ссылка на видео с youtube.com")
    special_blocks = models.ManyToManyField(
        SpecialBlock,
        verbose_name=u'Спецблоки',
        blank=True,
        related_name='news'
    )
    user = models.ForeignKey(User, verbose_name="Пользователь", blank=True, null=True,
                             on_delete=models.SET_NULL)
    modified_value = models.DateTimeField('Изменено', auto_now=True)

    objects = PublishManager()

    @staticmethod
    def unpublished_stat():
        return News.objects.filter(published=False).count()

    def __str__(self):
        return self.title

    def admin_cover(self):
        cover = self.get_cover()
        if cover:
            return mark_safe('<img width="120" src="/site_media/{}">'.format(cover))
        else:
            return None

    def get_pubdate(self):
        if self.delayed_publication:
            return mark_safe('<img width="10" src="/static/icons/unpublish_news.gif"> {}'
                             .format(f'{self.pubdate.strftime(format="%d.%m.%Y  %H:%M")}'))
        elif not self.published:
            return mark_safe('✘ {}'.format(f'{self.pubdate.strftime(format="%d.%m.%Y  %H:%M")}'))
        else:
            return mark_safe('✓ {}'.format(f'{self.pubdate.strftime(format="%d.%m.%Y  %H:%M")}'))

    def get_date_for_sorted(self):
        # Для сортировки новостей и статей в одном qs, в хронологическом порядке
        return self.pubdate.date()

    def save(self, *args, **kwargs):
        self.text = clean_word(self.text)
        self.text = seo_clean_content(self.text)
        self.text = sanitize_html(self.text)
        super(News, self).save()

    def title_and_text(self):
        return "%s\n%s" % (self.title, self.text)

    def content_type(self):
        pass
        # return ContentType.objects.get_for_model(self)

    def text_parts(self):
        if self.text.find('</p>') > -1:
            ind = self.text.find('</p>') + 4
            return [self.text[:ind], self.text[ind:]]
        return [self.text, ]
        # return u"Новости"

    def get_absolute_url(self):
        return reverse('news:detail',
                       args=[self.pk])

    def get_image(self):
        ''' @return image '''
        if self.is_main:
            image = self.get_bigpreview()
        else:
            image = self.get_smallpreview()

        return image

    def get_cover(self):
        if self.get_toppicture():
            return self.get_toppicture()
        else:
            # cover = NewsPhoto.objects.filter(news=self)
            cover = self.newsphoto_set.all()
            if len(cover):
                cover = cover[0]
            return cover

    def get_comment_count(self):
        # count = cache.get("news_%d_comments_count" % self.id)
        # if count is None:
        # cache.set("news_%d_comments_count" % self.id, count, 60 * 60)
        count = NewsNewComment.objects.only("object_id") \
            .filter(object_id=self.id).count()
        return count

    def get_normal_photos(self):
        qs = self.newsphoto_set.all().exclude(photo_type__in=[2, 3, 4])
        return qs

    def _get_somepicture(self, photo_type):
        p_filter = {
            'news': self,
            'photo_type': photo_type
        }

        p = NewsPhoto.objects.filter(**p_filter)

        if p.count() > 0:
            return p[0]
        else:
            try:
                # for old news picture models
                photo_model = NewsPhoto._get_photo_model(photo_type)
                tp = photo_model.objects.get(news=self)
                p_filter['image'] = tp.image
                if hasattr(tp, 'description'):
                    p_filter['description'] = tp.description
                p = NewsPhoto(**p_filter)
                p.save()
                # tp.delete()
                return p
            except:
                return None

    def get_toppicture(self):
        return self._get_somepicture(NewsPhoto.TOPPICTURE_TYPE)

    def get_bottompicture(self):
        return self._get_somepicture(NewsPhoto.BOTTOMPICTURE_TYPE)

    def get_smallpreview(self):
        return self._get_somepicture(NewsPhoto.SMALLPREVIEW_TYPE)

    def get_bigpreview(self):
        return self._get_somepicture(NewsPhoto.BIGPREVIEW_TYPE)

    def get_comments(self):
        """ Only treads roots. Not all comments """
        return NewsNewComment.objects.filter(
            object_id=self.id,
            parent=None,
            moderated=True
        ).order_by("-created")

    def is_photogallery(self):
        if self.newsphoto_set.all().count() > 1:
            return True
        else:
            return False

    @property
    def type_content(self):
        return 'Новость'

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = u"Новости"
        ordering = ('-pubdate',)

    @classmethod
    def special_blocks_changed(cls, **kwargs):
        # Update news special blocks lastnews_date
        for s in kwargs['instance'].special_blocks.all():
            s.save()


signals.m2m_changed.connect(
    News.special_blocks_changed,
    sender=News.special_blocks.through
)


class Article(TimeStampMixin, CountVisitMixin, FakeVisitMixin, models.Model):
    title = models.CharField(
        verbose_name=u'Заголовок', max_length=200)
    subtitle = models.CharField(
        verbose_name=u'Подзаголовок',
        max_length=200,
        blank=True,
        null=True
    )

    text = HTMLField('Тескт')

    pubdate = models.DateTimeField(
        verbose_name="Дата публикаци", auto_created=True)
    countries = models.ManyToManyField(
        Country, verbose_name='Страны', blank=True)
    script_country = models.ForeignKey(Country,
                                       verbose_name=u'Виджет скрипт для страны',
                                       blank=True, null=True,
                                       related_name='article_script_country',
                                       on_delete=models.SET_NULL)
    rubrics = models.ManyToManyField(
        Rubric,
        verbose_name='Рубрики',
    )
    special_blocks = models.ManyToManyField(
        SpecialBlock,
        verbose_name=u'Спецблоки',
        blank=True,
        related_name='articles'
    )
    published = models.BooleanField(verbose_name=u'Опубликовано', default=False,
                                    db_index=True)
    user = models.ForeignKey(User, verbose_name="Пользователь", blank=True, null=True,
                             on_delete=models.SET_NULL)
    rss_exclude = models.BooleanField('Исключить из RSS', default=False)

    class Meta:
        db_table = 'articles_article'
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ('-pubdate',)

    def __str__(self):
        return self.title

    def save(self):
        super(Article, self).save()
        # Обновляем кеш
        for rubric in self.rubrics.all():
            count = Article.objects.filter(rubrics=rubric, published=True).count()
            cache.set('rubric_%d_count_article' % rubric.id, count, 3 * 60 * 60)

    def title_and_text(self):
        return "%s\n%s" % (self.title, self.text)

    def text_parts(self):
        if self.text.find('</p>') > -1:
            ind = self.text.find('</p>') + 4
            return [self.text[:ind], self.text[ind:]]
        return [self.text, ]

    def get_absolute_url(self):
        return reverse_lazy("articles:detail", args=(self.id,))

    def get_image(self):
        """@return image"""
        return self.get_cover()

    def get_cover(self):
        images = ArticleImage.objects.filter(article=self)

        if len(images):
            cover = images[0].image
        else:
            cover = ''

        return cover

    def get_date_for_sorted(self):
        # Для сортировки новостей и статей в одном qs, в хронологическом порядке
        return self.pubdate.date()

    @classmethod
    def special_blocks_changed(cls, **kwargs):
        # Update news special blocks lastnews_date
        for s in kwargs['instance'].special_blocks.all():
            s.save()

    @property
    def type_content(self):
        return 'Статья'


signals.m2m_changed.connect(
    Article.special_blocks_changed,
    sender=Article.special_blocks.through
)


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    image = models.ImageField(
        verbose_name='Изображение статьи', upload_to="articles")
    description = models.CharField(
        verbose_name='Описание',
        blank=True,
        null=True,
        max_length=200
    )

    class Meta:
        verbose_name = "Изображения статьи"
        verbose_name_plural = "Изображения статей"

    def save(self, **kwargs):
        self.image.name = translify(self.image.name)
        super(ArticleImage, self).save(**kwargs)
        resize_image(
            os.path.join(settings.MEDIA_ROOT, self.image.name),
            settings.MAX_PHOTO_WIDTH,
            settings.MAX_PHOTO_HEIGHT
        )

    def __str__(self):
        return u'%s' % self.description


class NewsPhoto(ImageModel):
    DEFAULT_PICTURE_TYPE = 0
    TOPPICTURE_TYPE = 1
    SMALLPREVIEW_TYPE = 2
    BIGPREVIEW_TYPE = 3
    BOTTOMPICTURE_TYPE = 4

    PHOTO_TYPE_CHOICES = (
        (DEFAULT_PICTURE_TYPE, u'---'),
        (TOPPICTURE_TYPE, u'Верхнее фото'),
        (SMALLPREVIEW_TYPE, u'Маленькое превью'),
        (BIGPREVIEW_TYPE, u'Большое превью'),
        (BOTTOMPICTURE_TYPE, u'Нижнее фото'),
    )

    # for compatibility
    PHOTO_TYPE_MODELS = (
        (TOPPICTURE_TYPE, 'NewsTopPicture'),
        (SMALLPREVIEW_TYPE, 'NewsSmallPreview'),
        (BIGPREVIEW_TYPE, 'NewsBigPreview'),
        (BOTTOMPICTURE_TYPE, 'NewsBottomPicture'),
    )

    PHOTO_TYPE_SIZE = (  # for cropping
        (DEFAULT_PICTURE_TYPE,
         (
             settings.MAX_PHOTO_WIDTH,
             settings.MAX_PHOTO_HEIGHT
         )),
        (TOPPICTURE_TYPE,
         (
             settings.MAX_PHOTO_WIDTH,
             settings.MAX_PHOTO_HEIGHT
         )),
        (SMALLPREVIEW_TYPE, (80, 80)),
        (BIGPREVIEW_TYPE, (160, 120)),
        (BOTTOMPICTURE_TYPE,
         (
             settings.MAX_PHOTO_WIDTH,
             settings.MAX_PHOTO_HEIGHT
         )),
    )

    news = models.ForeignKey(News, on_delete=models.CASCADE)
    photo_type = models.SmallIntegerField(
        verbose_name=u'Тип фото',
        choices=PHOTO_TYPE_CHOICES,
        default=0
    )
    description = models.CharField(
        verbose_name=u'Описание',
        blank=True,
        null=True,
        max_length=200
    )

    class Meta:
        verbose_name = u"Фотография новости"
        verbose_name_plural = u"Фотографии новости"

    def save(self):
        self.image.name = translify(self.image.name)
        super(NewsPhoto, self).save()
        # resize_image(
        #     os.path.join(settings.MEDIA_ROOT, self.image.name),
        #     self._get_photo_type_size(self.photo_type)[0],
        #     self._get_photo_type_size(self.photo_type)[1]
        # )

    def __str__(self):
        return u'%s' % self.image

    @staticmethod
    def _get_photo_model(photo_type):
        import tourprom as tp
        if photo_type in dict(NewsPhoto.PHOTO_TYPE_CHOICES).keys():
            photo_model_name = dict(NewsPhoto.PHOTO_TYPE_MODELS)[photo_type]
            try:
                photo_model = getattr(tp.news.models, photo_model_name)
                return photo_model
            except:
                pass

        return None

    @staticmethod
    def _get_photo_type_size(photo_type):
        if photo_type in dict(NewsPhoto.PHOTO_TYPE_CHOICES).keys():
            return dict(NewsPhoto.PHOTO_TYPE_SIZE)[photo_type]

        return None

    def get_image(self):
        ''' @return url to image '''
        if image_exists(self.image):
            return self.image.url
        else:
            return os.path.join(settings.MEDIA_URL, "images/news/noimage.jpg")


class NewsSmallPreview(ImageModel):
    news = models.OneToOneField(
        News,
        verbose_name=u'Новость',
        primary_key=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = u"Маленькое превью"
        verbose_name_plural = u"Маленькое превью"

    def get_image(self):
        ''' @return url to image '''
        if image_exists(self.image):
            return self.image.url
        else:
            return os.path.join(
                settings.MEDIA_URL,
                "images/news/noimage-80x80.jpg"
            )

    def save(self):
        self.image.name = tp_translify(self.image.name)
        super(NewsSmallPreview, self).save()
        resize_image_hard(
            os.path.join(settings.MEDIA_ROOT, self.image.name), 80, 80)


class NewsBigPreview(ImageModel):
    news = models.OneToOneField(
        News,
        verbose_name=u'Новость',
        primary_key=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = u"Большое превью"
        verbose_name_plural = u"Большое превью"

    def save(self):
        self.image.name = translify(self.image.name)
        super(NewsBigPreview, self).save()
        resize_image_hard(
            os.path.join(settings.MEDIA_ROOT, self.image.name), 160, 120)

    def get_image(self):
        ''' @return url to image '''
        if image_exists(self.image):
            return self.image.url
        else:
            return os.path.join(
                settings.MEDIA_URL,
                "images/news/noimage-160х120.jpg"
            )


class NewsTopPicture(ImageModel):
    news = models.OneToOneField(
        News,
        verbose_name=u'Новость',
        primary_key=True, on_delete=models.CASCADE
    )
    description = models.CharField(
        verbose_name='Подпись',
        max_length=200,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = u"Верхнее фото"
        verbose_name_plural = u"Верхнее фото"

    def save(self):
        self.image.name = tp_translify(self.image.name)
        super(NewsTopPicture, self).save()
        resize_image(
            os.path.join(settings.MEDIA_ROOT, self.image.name), 800, 0)


class NewsBottomPicture(ImageModel):
    news = models.OneToOneField(
        News,
        verbose_name=u'Новость',
        primary_key=True, on_delete=models.CASCADE
    )
    description = models.CharField(
        verbose_name=u'Подпись',
        max_length=200,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = u"Нижнее фото"
        verbose_name_plural = u"Нижнее фото"

    def save(self):
        self.image.name = transliterate(self.image.name)
        super(NewsBottomPicture, self).save()
        resize_image(
            os.path.join(
                settings.MEDIA_ROOT,
                transliterate(self.image.name)
            ),
            800,
            0
        )


class NewsCommentManager(TreeManager):
    def get_query_set(self):
        ctype = ContentType.objects.get_for_model(News)
        qs = super(NewsCommentManager, self).get_query_set().filter(
            content_type=ctype
        )
        return qs


class NewsNewComment(Comment):
    objects = NewsCommentManager()

    def save(self, *args, **kwargs):
        from comments.utils import filter_bad_words
        if not self.id:
            ctype = ContentType.objects.get_for_model(News)
            self.content_type = ctype

        self.text = filter_bad_words(self.text)
        self.text = clean_word(self.text)
        self.text = seo_clean_content(self.text)
        self.text = sanitize_html_comment(self.text)

        return super(NewsNewComment, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u"Комментарий к новости"
        verbose_name_plural = u"Комментарии к новости"
        proxy = True
