from datetime import datetime
from random import randrange, seed as randseed

from django.apps import apps
from django.core.cache import cache
from django.db import models

from core.templatetags.tags_utils import class_name
from core.utils import start_date_of_this_week

SECONDS_PER_DAY = 24 * 60 * 60


class CountVisitMixin(models.Model):
    count_visits = models.PositiveIntegerField(
        verbose_name='Счетчик просмотров',
        default=0,
        editable=False
    )

    def update_count_visits(self):
        model = apps.get_model(self._meta.app_label, self._meta.object_name)
        result = model.objects.filter(id=self.id).update(
            count_visits=models.F('count_visits') + 1
        )
        # print(result)

    class Meta:
        abstract = True


class FakeVisitMixin(models.Model):
    FAKE_VISITS_RANGE = (0, 3)
    VISITS_CACHE_DELAY = 760

    fake_visits = models.PositiveIntegerField(
        verbose_name="Псевдо",
        default=0
    )

    def get_visits(self):
        from django.core.cache import cache
        cache_key = self.__class__.__name__ + "." + str(self.id) + ".fk_visits"
        visits = cache.get(cache_key)

        if not visits:
            cache.set(cache_key, self.fake_visits, self.VISITS_CACHE_DELAY)
            visits = self.fake_visits

        return visits

    def update_fake_visits(self):
        randseed(datetime.now())
        fake_visit_add = randrange(self.FAKE_VISITS_RANGE[0],
                                   self.FAKE_VISITS_RANGE[1] + 1)

        model = apps.get_model(self._meta.app_label, self._meta.object_name)
        model.objects.filter(id=self.id).update(
            fake_visits=models.F('count_visits') * 2
        )
        # model.objects.filter(id=self.id).update(
        #     fake_visits=models.F('fake_visits') * 2
        # )
        # print('fake_visits*2')

    def save(self, **kwargs):
        if self.fake_visits == 0:
            self.fake_visits = self.count_visits

        super(FakeVisitMixin, self).save(**kwargs)

    class Meta:
        abstract = True


class VisitsMixin(object):
    # не забудь добавить где-то во вьюхе вызов метода add_visit()

    def get_all_visited_this_week(self):
        cache_key_wildcard = self._get_visits_cache_key(
            id="*", date=start_date_of_this_week())

        obj_ids = []
        try:
            keys = cache.keys(cache_key_wildcard)
        except Exception as ex:
            print(ex)
            keys = []

        for key in keys:
            full_key = "visits:%s:%s" % (class_name(self), key)

            obj_ids.append(self._get_id_from_key(full_key))

        return obj_ids

    def get_visits(self):
        return self.count_visits

    def get_visits_this_week(self):
        cache_key = self._get_visits_cache_key(date=start_date_of_this_week())
        week_visits = cache.get(cache_key)

        if week_visits:
            return (self.count_visits - week_visits)
        else:
            return 0

    # def get_visits_this_month(self):
    #     dt = datetime.today()
    #     date = datetime(day=1, year=dt.year, month=dt.month)
    #     cache_key = self._get_visits_cache_key(date=date)
    #     month_visits = cache.get(cache_key)
    #     if month_visits:
    #         return (self.count_visits - month_visits)
    #     else:
    #         return 0

    def add_visit(self):
        if hasattr(self, 'count_visits'):
            # this only applies to current object, not updates database
            self.count_visits += 1

            # this updates database (self.save() is not the best solutions because of redundant query)
            type(self).objects.filter(pk=self.pk).update(
                count_visits=models.F('count_visits') + 1)

            self.write_monday_visits()

        if hasattr(self, 'resort') and class_name(self.resort) == 'Resort':
            self.resort.add_visit()
        elif hasattr(self, 'region') and class_name(self.region) == 'Region':
            self.region.add_visit()
        elif hasattr(self, 'country') and class_name(self.country) == 'Country':
            self.country.add_visit()

    @staticmethod
    def _get_id_from_key(cache_key):
        return int(cache_key.split(":")[-2])

    def _get_visits_cache_key(self, key_name='visits', id=None, date=datetime.today()):
        # key example for Country with id=2:
        # "visits:Country:2:09.05.2016"

        if id is None:
            id = self.id

        cache_key = "%s:%s:%s:%s" % (
            key_name,
            class_name(self),
            id,
            datetime.strftime(date, "%d.%m.%Y")
        )
        return cache_key

    def write_monday_visits(self):
        """ write total visit count on first visit in monday """
        if self.get_visits_this_week() == 0:
            cache_key = self._get_visits_cache_key(date=start_date_of_this_week())
            cache.set(cache_key, self.count_visits, 8 * SECONDS_PER_DAY)

    # def write_month_visits(self):
    #     """ write total visit count on first visit in first day of month """
    #     if datetime.today().date().day == 1 and not cache.get(self._get_visits_cache_key()):
    #         cache.set(self._get_visits_cache_key(), self.count_visits, 32*SECONDS_PER_DAY)


class TimeStampMixin(models.Model):
    """ Абстрактная модель для TimeStampMixin"""
    created = models.DateTimeField(
        verbose_name='Создан', auto_now_add=True,
        blank=True
    )
    modified = models.DateTimeField(
        verbose_name='Отредактирован',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True


BLOCK_IP_FOR_PAGE_DELAY = 1800


class UpdateCountVisitsViewMixin(object):
    def get_context_data(self, **kwargs):
        self.object.update_count_visits()
        return super(
            UpdateCountVisitsViewMixin, self).get_context_data(**kwargs)


class UpdateFakeVisitsViewMixin(object):
    def is_client_ip_uniq(self):
        from django.core.cache import cache

        ip = get_client_ip(self.request)
        path = self.request.path

        cache_key = u"visit%s.%s" % (ip, path)

        already_visited = cache.get(cache_key)

        if already_visited:
            return False
        else:
            cache.set(cache_key, True, BLOCK_IP_FOR_PAGE_DELAY)
            return True

    def get_context_data(self, **kwargs):
        if self.is_client_ip_uniq():
            self.object.update_fake_visits()

        return super(
            UpdateFakeVisitsViewMixin, self).get_context_data(**kwargs)


class VisitViewMixin(UpdateCountVisitsViewMixin, UpdateFakeVisitsViewMixin):
    pass


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
