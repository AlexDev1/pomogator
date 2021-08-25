# coding=utf-8

from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes import fields as generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

# from tourprom.custom_utils.templatetags.custom_utils import class_name

__all__ = [
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
    "REVIEW_MONTHS",
    "REVIEW_YEARS",
    "SHIPS_DECK",
    "STATUS_CONSTRUCTIVE",
    "STATUS_THANKS",
    "STATUS_COMPLAINT",
    "STATUS_SPAM",
    "REVIEW_STATUS",
    "POI_DESCRIPTION_NODE",
    "RESORT_DESCRIPTION_NODE",
    "COUNTRY_POI_NODE",
    "RESORT_POI_NODE",
    "REGION_POI_NODE",
    "SECONDS_PER_DAY",
    "Votable",
    "Draft",
]

# TODO: use calendar.month_name[mont_number] instead
JANUARY = 1
FEBRUARY = 2
MARCH = 3
APRIL = 4
MAY = 5
JUNE = 6
JULY = 7
AUGUST = 8
SEPTEMBER = 9
OCTOBER = 10
NOVEMBER = 11
DECEMBER = 12

REVIEW_MONTHS = (
    (JANUARY, u'январь'),
    (FEBRUARY, u'февраль'),
    (MARCH, u'март'),
    (APRIL, u'апрель'),
    (MAY, u'май'),
    (JUNE, u'июнь'),
    (JULY, u'июль'),
    (AUGUST, u'август'),
    (SEPTEMBER, u'сентябрь'),
    (OCTOBER, u'октябрь'),
    (NOVEMBER, u'ноябрь'),
    (DECEMBER, u'декабрь'),
)

REVIEW_YEARS = tuple(
    (year, '%s' % year) for year in range(
        datetime.now().year,
        datetime.now().year - 16, -1
    )
)

SHIPS_DECK = (
    (1, u'I-палубные'),
    (2, u'II-палубные'),
    (3, u'III-палубные'),
    (4, u'IV-палубные'),
    (5, u'V-палубные')
)

STATUS_CONSTRUCTIVE = '1'
STATUS_THANKS = '2'
STATUS_COMPLAINT = '3'
STATUS_SPAM = '4'

REVIEW_STATUS = (
    (STATUS_CONSTRUCTIVE, 'конструктивный отзыв'),
    (STATUS_THANKS, 'благодарность'),
    (STATUS_COMPLAINT, 'жалоба'),
    (STATUS_SPAM, 'спам')
)

# Content Nodes IDs
POI_DESCRIPTION_NODE = 8
RESORT_CONTENT_DESCRIPTION_NODE = 9
RESORT_DESCRIPTION_NODE = 9
COUNTRY_POI_NODE = 143
COUNTRY_CONTENT_GENERAL_INFO_ID = 42
REGION_CONTENT_DESCRIPTION_ID = 114
RESORT_POI_NODE = 146
REGION_POI_NODE = 163

SECONDS_PER_DAY = 24 * 60 * 60

RUSSIAN_REGION_RUBRIC_ID = 40
ALL_HOTELS_RUBRIC_ID = 8
RUSSIAN_HOTELS_RUBRIC_ID = 41
NON_RUSSIAN_HOTELS_RUBRIC_ID = 42


class Votable(models.Model):
    """Абстрактная модель для реализации голосов за и против"""

    voteups = models.IntegerField(
        u'Количесвто лайков', editable=False, default=0)
    votedowns = models.IntegerField(
        u'Количесвто дислайков', editable=False, default=0)

    class Meta:
        abstract = True

    def recount_votes(self):
        ctype = ContentType.objects.get_for_model(self)
        from core.models import Vote
        votes = Vote.objects.filter(content_type=ctype, object_id=self.id)
        ups = votes.filter(like__gt=0).count()
        downs = votes.filter(like__lt=0).count()
        self.__class__.objects.filter(id=self.id) \
            .update(voteups=ups, votedowns=downs)


class Draft(models.Model):
    """For autosaving drafts for reviews on different types of content"""

    user = models.ForeignKey(
        User, related_name='drafts', verbose_name=u'Пользователь', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, verbose_name=u'Тип объекта', on_delete=models.CASCADE)
    object_id = models.IntegerField(verbose_name=u'Объект')
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    updated = models.DateTimeField(u'Дата', auto_now=True)
    data = models.TextField(u'Данные')

    def __str__(self):
        return u'%s' % self.content_object

    class Meta:
        app_label = 'countries'
