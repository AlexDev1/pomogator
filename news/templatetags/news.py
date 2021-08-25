from datetime import datetime, timedelta

from django import template

from news.models import News, Article, SpecialBlock, Stories

register = template.Library()


@register.inclusion_tag('news/blocks/top_news.html', takes_context=True)
def top_news(context, count=None):
    # нужно уравновесить количество информеров и новостей на главной странице
    # Количество информеров передаётся через кэш
    # (в теге advertisers.templatetags.adv_content.top_informers)
    one_top_main_news = News.objects.filter(
        published=True,
    ).order_by("-pubdate")[:15]

    context['object_list'] = one_top_main_news
    return context


@register.inclusion_tag(
    'news/blocks/_top_articles.html', takes_context=True)
def top_articles(context, count=5):
    object_list = Article.objects.filter(published=True) \
                      .order_by("-pubdate")[:count]

    context['object_list'] = object_list
    return context


@register.inclusion_tag(
    'news/blocks/top_specialblocks.html', takes_context=True)
def top_specialblocks(context):
    specialblock_actual_days = 30
    from_date = datetime.now() - timedelta(days=specialblock_actual_days)
    list_item = SpecialBlock.objects.filter(
        lastnews_date__gt=from_date)
    context['object_list'] = SpecialBlock.objects.filter(
        lastnews_date__gt=from_date)
    return context


@register.inclusion_tag(
    'news/blocks/top_topic_day_news.html', takes_context=True)
def top_topics_day_news(context, news_block=None):
    """
    Шаблонный тег для вывода ТЕМ ДНЯ, если приходить параметр news_block показываем главную новость, для главной страницы
    :param context:
    :param news_block:
    :return:
    """
    if news_block:
        object_list = News.objects.filter(published=True, is_main=True).order_by("-pubdate")[:3]
        context['news_block'] = True
        context['object'] = object_list[0]
        context['topics_carousel'] = 'topics-carousel-main'
    else:
        context['topics_carousel'] = 'topics-carousel'
    topics = Stories.objects.filter(active=True).order_by('order')
    context.update({'topics': topics})
    return context


@register.inclusion_tag(
    'news/blocks/top_news_subject.html', takes_context=True)
def top_news_subject(context, subject, count=10):
    # Топ новостей по сюжетам
    object_list = News.objects.filter(published=True, subject=subject) \
                      .order_by("-pubdate")[:count]

    context['object_list'] = object_list
    context['subject'] = subject
    return context
