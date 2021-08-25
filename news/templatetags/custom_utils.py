from __future__ import unicode_literals, print_function

import json
import logging
from calendar import month_name as calendar__month_name

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import date as dj_date_filter, stringfilter
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from jsmin import jsmin
from tinymce import settings as mce_settings

log = logging.getLogger(__name__)

register = template.Library()


@register.filter
def class_name(obj):
    return obj.__class__.__name__


@register.filter
def rst_half(lst):
    half = len(lst) / 2
    return lst[:half]


@register.filter
def rst_half_1(lst):
    try:
        half = len(lst) / 2
        return lst[:half + 1]
    except TypeError:
        return ''


@register.filter
def second_half(lst):
    half = len(lst) / 2
    return lst[half:]


@register.filter
def second_half_1(lst):
    half = len(lst) / 2
    return lst[half + 1:]


@register.filter
def latter_half(lst):
    half = len(lst) / 2
    return lst[half:]


@register.filter
def one_third_count(lst):
    third = len(lst) / 3
    return third


@register.filter
def two_thirds_count(lst):
    third = (len(lst) / 3) * 2
    return third


@register.filter
def latter_half_1(lst):
    try:
        half = len(lst) / 2
        return lst[half + 1:]
    except TypeError:
        return ''


@register.inclusion_tag('includies/paginator.html', takes_context=True)
def paginator2(context, page):
    """
    Is a modification of news.templatetags.blocks_redesign.paginator
    but without 'sort' and 'filter'
    """
    current = page.number
    total = page.paginator.num_pages
    begin, middle, end = [], [], []
    if current > 5:
        begin = range(1, 3)
        if total - current > 4:
            middle = range(current - 2, current + 3)
            end = range(total - 1, total + 1)
        else:
            end = range(current - 2, total + 1)
    else:
        if total - current > 4:
            begin = range(1, current + 3)
            end = range(total - 1, total + 1)
        else:
            begin = range(1, total + 1)

    return {
        'request': context['request'],
        'page': page,
        'begin': begin,
        'middle': middle,
        'end': end
    }


# @register.simple_tag
# def admin_url(obj):
#     return get_admin_url(obj, obj.id)


@register.filter
def vreplace(text, tpl):
    tpl_1, tpl_2 = tpl.split("|")
    return text.replace(tpl_1, tpl_2)


@register.filter
def partition_old(thelist, n):
    """
    From https://djangosnippets.org/snippets/6/

    Break a list into ``n`` pieces. The last list may be larger
    than the rest if the list doesn't break cleanly. That is::

        >>> l = range(10)

        >>> partition(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> partition(l, 3)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8, 9]]

        >>> partition(l, 4)
        [[0, 1], [2, 3], [4, 5], [6, 7, 8, 9]]

        >>> partition(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]

    p = len(thelist) / n

    list_len = len(thelist)
    split = list_len // n
    if list_len % n != 0:
        split += 1

    return [thelist[p * i:p * (i + 1)] for i in range(n - 1)] + [thelist[p * (i + 1):]]


@register.filter
def partition(thelist, n):
    """
    tamplate tag partition doesn't work correctly for array with one element,
    so this new partition template tag was added.
    You can use it like:
    {% for part in mylist|partition:2 %}
        {% for item in part %}
            do something with item
        {% endfor %}
    {% endfor %}
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]

    list_len = len(thelist)

    split = list_len / n

    if list_len % n != 0:
        split += 1

    out = []
    for i in range(n):
        begin = i * split
        end = begin + split
        item = thelist[int(begin):int(end)]
        out.append(item)

    return out


partition_new = partition


@register.filter
def tag_list(html, tagname=["p", "ul", "ol"]):
    """ Split html to list of bloks """
    from bs4 import BeautifulSoup

    bs = BeautifulSoup(html)
    return map(lambda s: s.__str__(), bs.findAll(tagname)) or [html]


@register.filter
def parts(arr, item_count=1):
    from math import ceil

    if len(arr) <= item_count:
        return arr

    part_count = int(ceil(len(arr) / float(item_count)))

    parts = []
    print("PART", len(arr), item_count, part_count)
    for i in range(1, part_count + 1):
        start = (i - 1) * item_count
        end = i * item_count
        part = arr[start:end]
        print("PART #", i, start, end, part)
        parts.append(part)

    return parts


@register.filter
@stringfilter
def rupluralize(value, endings):
    """
    Russian words pluralize
    This code based on https://djangosnippets.org/snippets/1714/ and comments.
    USAGE:
    {{ comments|length }} комментари{{ comments|length|rupluralize:"й,я,ев" }}
    """
    try:
        endings = endings.split(',')
        value = int(value)
        if value % 100 in (11, 12, 13, 14):
            return endings[2]
        if value % 10 == 1:
            return endings[0]
        if value % 10 in (2, 3, 4):
            return endings[1]
        else:
            return endings[2]
    except:
        raise template.TemplateSyntaxError


@register.filter
def humanized_date(dt, tpl):
    return dj_date_filter(dt, tpl)


@register.filter
def month_name(month_number):
    return calendar__month_name[month_number]


@register.filter
def month_name_ru(month_number):
    return ru_month_name()[month_number - 1]


@register.filter
def grid_col(element_count):
    count = int(element_count)
    grid_col = int(12 / count)
    return grid_col


@register.filter
@stringfilter
def balance_title_n_text(text, title, char_count=250):
    return text[:(char_count - len(title))]


@register.filter
@stringfilter
def balance_title_n_text2(text, title):
    title_font_size = 2  # <h2>, <h3> ~ (normal_font_size * 2)
    title_len = len(title) * title_font_size
    return text[:-title_len]


@register.filter
def space_after_comma(text):
    return text.replace(",", ", ")


@register.filter
def space_around_hyphen(text):
    return text.replace("-", " - ")


@register.filter
def space_around_plus(text):
    return text.replace("+", " + ")


@register.filter(name='has_group')
def has_group(user, group_name):
    from django.contrib.auth.models import Group
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        print('Group except DoesNotExist: {}'.format(group_name))
        return False
    # print(group in user.groups.all())
    return group in user.groups.all()


@register.filter()
def filter_pubdate(qs, pubdate):
    filtered_qs = qs.filter(pubdate=pubdate)
    return filtered_qs


@register.simple_tag
def current_year():
    from datetime import datetime
    return datetime.today().year


@register.filter()
def push_zeroes(number, zeroes_num):
    str = u'%d' % number
    out = str
    if len(str) <= zeroes_num:
        diff = zeroes_num - len(str)
        out = ''
        out = '0' * diff
        out += str

    return out


@register.tag
def textareas_mce(parser, token):
    mce_config = mce_settings.CONFIG.copy()
    config = json.dumps(mce_config, cls=DjangoJSONEncoder)[1:-1]
    callbacks = mce_settings.CALLBACKS.copy()
    callbacks['file_browser_callback'] = 'djangoFileBrowser'

    html = jsmin(render_to_string('tinymce/tinymce_init.js',
                                  context={'callbacks': callbacks,
                                           'tinymce_config': config}))
    return html


@register.simple_tag
def unpublished_news(model='News'):
    from news.models import News, Article
    if model == 'News':
        count = News.objects.unpublished_count()
    elif model == 'Article':
        count = Article.objects.filter(published=False).count()
    else:
        return None
    if count > 0:
        color = '#ff8800'
    else:
        color = 'None'
    return mark_safe('<small style="background-color: {};padding: 3px;">{}</smal>'.format(color, count))


@register.simple_tag
def delayed_publication_news():
    from news.models import News
    return News.objects.all_objects().filter(delayed_publication=True, published=False).count()
