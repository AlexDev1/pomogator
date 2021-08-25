from __future__ import unicode_literals

import logging
import time
from collections import OrderedDict
from datetime import tzinfo, timedelta
from mimetypes import guess_type

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.feedgenerator import Enclosure
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import strip_tags
from django.utils.xmlutils import SimplerXMLGenerator

from news.models import News, NewsPhoto

log = logging.getLogger(__name__)


def full_site_url(path):
    # use instead request.build_absolute_uri() for https in url
    # without SECURE_PROXY_SSL_HEADER settings
    return settings.SITE_URL + path


class DjangoTimezone(tzinfo):
    """
    Временная зона, используемая сейчас в настройке TIME_ZONE Django.
    Поскольку возвращаемое из базы значение даты имеет т.н. "наивный формат",
    т.е. указание о зоне не содержит, эта временная зона, при необходимости,
    может использоваться для его "дополнения", т.к. точно ему соответствует.
    Например, это полезно при выдаче новостей в RSS'е.
    """

    ZERO = timedelta(0)
    HOUR = timedelta(hours=1)

    def __init__(self):
        self.STDOFFSET = timedelta(seconds=-time.timezone)
        if time.daylight:
            self.DSTOFFSET = timedelta(seconds=-time.altzone)
        else:
            self.DSTOFFSET = self.STDOFFSET

        self.DSTDIFF = self.DSTOFFSET - self.STDOFFSET

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self.DSTOFFSET
        else:
            return self.STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return self.DSTDIFF
        else:
            return self.ZERO

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0


class SXG(SimplerXMLGenerator):
    """Добавляет в syndication возможность создавать элементы с CDATA."""

    def addQuickElementCDATA(self, name, contents=None, attrs=None):
        if attrs is None:
            attrs = {}
        self.startElement(name, attrs)
        if contents is not None:
            self._write('<![CDATA[' + contents + ']]>')
        self.endElement(name)


class RSSFeed(Rss201rev2Feed):

    def add_root_elements(self, handler):
        """Патч, в django 2.1 обнаружен баг, подробности:
           https://code.djangoproject.com/ticket/14202.
        """
        handler.addQuickElement(u"title", self.feed['title'])
        handler.addQuickElement(u"link", self.feed['link'])
        handler.addQuickElement(u"description", self.feed['description'])

        """ Конец патча"""

        handler.startElement(u"image", {})
        handler.addQuickElement(u"url", self.feed['image_url'])
        handler.addQuickElement(u"title", self.feed['title'])
        handler.addQuickElement(u"link", self.feed['link'])
        handler.endElement(u"image")

    def add_item_elements(self, handler, item):
        super(RSSFeed, self).add_item_elements(handler, item)
        if 'enclosures' in item.keys() and item['enclosures']:
            if not item['enclosures']:
                exist_enclosures = []
                for encl in item['enclosures']:
                    data = {
                        u"url": encl.url,
                        u"length": encl.length,
                        u"type": encl.mime_type
                    }
                    if data['url'] not in exist_enclosures:
                        exist_enclosures.append(data['url'])
                        handler.addQuickElement(u"enclosure", '', data)


class FullRSSFeed(RSSFeed):

    def write(self, outfile, encoding):
        handler = SXG(outfile, encoding)
        handler.startDocument()
        handler.startElement(u"rss", self.rss_attributes())
        handler.startElement(u"channel", self.root_attributes())
        self.add_root_elements(handler)
        self.write_items(handler)
        self.endChannelElement(handler)
        handler.endElement(u"rss")

    def add_item_elements(self, handler, item):
        handler.addQuickElementCDATA(u'description', item['description'])
        item['description'] = None
        super(FullRSSFeed, self).add_item_elements(handler, item)


class YandexFeed(RSSFeed):

    def add_root_elements(self, handler):
        super(YandexFeed, self).add_root_elements(handler)
        handler.addQuickElement(
            u"yandex:logo",
            self.feed['square_logo'],
            {u"type": u"square"}
        )

    def rss_attributes(self):
        rval = super(YandexFeed, self).rss_attributes()
        rval = OrderedDict(rval.items())
        rval['xmlns:yandex'] = "https://news.yandex.ru"
        return rval

    def add_item_elements(self, handler, item):
        super(YandexFeed, self).add_item_elements(handler, item)
        handler.addQuickElement("yandex:full-text", item['fulltext'])


class ZenYandexFeed(FullRSSFeed):
    def rss_attributes(self):
        attributes = {
            "version": self._version,
            "xmlns:atom": u"http://www.w3.org/2005/Atom",
            "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
            "xmlns:dc": "http://purl.org/dc/elements/1.1/",
        }
        return attributes

    def add_item_elements(self, handler, item):
        handler.addQuickElementCDATA('description', item['description'])
        handler.addQuickElementCDATA('content:encoded', item['fulltext'])
        item['description'] = None
        super(FullRSSFeed, self).add_item_elements(handler, item)


class MailRuFeed(FullRSSFeed):
    def rss_attributes(self):
        attributes = {
            "version": self._version,
            "xmlns:atom": u"http://www.w3.org/2005/Atom",
            "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
            "xmlns:dc": "http://purl.org/dc/elements/1.1/",
        }
        return attributes

    def add_item_elements(self, handler, item):
        handler.addQuickElementCDATA('description', item['description'])
        handler.addQuickElementCDATA('content:encoded', item['fulltext'])
        super(FullRSSFeed, self).add_item_elements(handler, item)


def get_enclosure(request, image):
    try:
        mime_type, mime_enc = guess_type(image.path)
        if mime_type is not None:
            return Enclosure(
                url=full_site_url(image.url),
                length=str(image.size),
                mime_type=mime_type
            )
    except OSError as ex_OS:
        print(ex_OS)
    except Exception as ex:
        print(ex)
    return None


def get_video_enclosure(video):
    # TODO: store size and mime_type with video
    """
    try:
        video_url = video.get_file_url()
        if video_url:
            file = video.videofile.storage
            mime_type, mime_enc = guess_type(video_url)
            size = 0
            return Enclosure(
                url=video_url, length=str(size), mime_type=mime_type)
    except:
        pass
    """
    return None


def populate_news_feed(feed, feed_name, request, lastweek=False):
    SITE_URL = request.build_absolute_uri()
    if lastweek:
        some_day_last_week = timezone.now().date() - timedelta(days=7)
        news = News.objects.filter(published=True, pubdate__gte=some_day_last_week, rss_exclude=False).order_by(
            '-pubdate')[:30]
    else:
        news = News.objects.filter(published=True, rss_exclude=False).order_by('-pubdate')[:30]

    for n in news:
        description = ""
        if feed_name == "rssfull":
            text = n.text
            description = text
        elif feed_name == "rssmailru":
            text = n.text
            description = strip_tags(n.text)[:480]
        else:
            text = strip_tags(n.text)
            if n.subtitle and len(n.subtitle) > 0:
                description = n.subtitle
            else:
                if text.find(".") > 0:
                    description = text[:text.find(".")]

        rubric = u"Новости"
        if len(n.rubrics.all()) > 0:
            rubric = n.rubrics.all()[0]

        enclosures = []
        if not feed_name == "yandex":
            if len(NewsPhoto.objects.filter(news=n).all()) > 0:
                encl = get_enclosure(request, n.get_cover().image)
                if encl:
                    enclosures.append(encl)

        if len(NewsPhoto.objects.filter(news=n).all()) > 0:
            encl = get_enclosure(request, n.get_cover().image)
            if encl and len(enclosures) < 1:
                enclosures.append(encl)

        django_tz = DjangoTimezone()
        # if len(enclosures) <= 1 else list(enclosures[0])
        feed.add_item(
            title=n.title,
            # link=request.build_absolute_uri(n.get_absolute_url()),
            link=full_site_url(n.get_absolute_url()),
            author_email=settings.FEEDBACK_EMAIL,
            author_name='Турпром',
            description=description,
            categories=[rubric, ],
            pubdate=n.pubdate.replace(tzinfo=django_tz),
            fulltext=text,
            enclosures=enclosures
        )

    return feed


def populate_articles_feed(feed, feed_name, request, now=False):
    SITE_URL = request.build_absolute_uri()
    from news.models import Article

    article_list = Article.objects.filter(published=True).order_by('-pubdate')[:10]

    for art in article_list:
        description = ""

        text = strip_tags(art.text)
        if art.subtitle and len(art.subtitle) > 0:
            description = art.subtitle
        else:
            if text.find(".") > 0:
                description = text[:text.find(".")]

        enc_img = art.get_cover()

        if not enc_img:
            user_logo = art.advertiser.get_logo()
            if hasattr(user_logo, 'image'):
                enc_img = user_logo.image

        if not enc_img:
            enclosures = []
        else:
            enclosure = get_enclosure(request, enc_img)
            enclosures = [enclosure]

        # django_tz = DjangoTimezone()

        feed.add_item(
            title=art.title,
            link=full_site_url(str(art.get_absolute_url())),
            description=description,
            author_email=settings.FEEDBACK_EMAIL,
            author_name='Турпром',
            # categories=[rubric, ],
            pubdate=art.pubdate,  # .replace(tzinfo=django_tz),
            fulltext=text,
            enclosures=enclosures
        )

    return feed


def show_feed(request, feed_name):
    SITE_URL = request.build_absolute_uri()
    feed_description = 'ЗОЖ-news: новости ЗОЖ и HLS, новости активити, правильной еды и HLS, науки и медицины '

    if feed_name == "yandex":
        feed = YandexFeed(
            title='Новости ЗОЖ',
            link=settings.SITE_URL,
            description=feed_description,
            image_url=full_site_url(
                settings.STATIC_URL + 'images/favicon.png'),
            square_logo=full_site_url(
                settings.STATIC_URL + 'images/favicon.png')
        )
        feed = populate_news_feed(feed, feed_name, request, lastweek=True)
        # feed = populate_articles_feed(feed, feed_name, request)
    elif feed_name == "rssfull":
        feed = FullRSSFeed(
            title='Главные новости ЗОЖ',
            link=SITE_URL,
            description=feed_description,
            image_url=full_site_url(settings.STATIC_URL + 'images/favicon.png')
        )
        feed = populate_news_feed(feed, feed_name, request)
        feed = populate_articles_feed(feed, feed_name, request)
    elif feed_name == "zen":
        feed = ZenYandexFeed(
            title='Главные новости ЗОЖ',
            link=settings.SITE_URL,
            description=feed_description,
            image_url=full_site_url(settings.STATIC_URL + 'images/favicon.png')
        )
        feed = populate_news_feed(feed, feed_name, request)
        feed = populate_articles_feed(feed, feed_name, request)
    elif feed_name == "rssmailru":
        feed = MailRuFeed(
            title='Главные новости ЗОЖ',
            link=settings.SITE_URL,
            description=feed_description,
            image_url=full_site_url(settings.STATIC_URL + 'images/favicon.png')
        )
        feed = populate_news_feed(feed, feed_name, request)
        feed = populate_articles_feed(feed, feed_name, request)
    else:
        feed = RSSFeed(
            title='Главные новости ЗОЖ',
            link=settings.SITE_URL,
            description=feed_description,
            image_url=full_site_url(settings.STATIC_URL + 'images/favicon.png')
        )
        feed = populate_news_feed(feed, feed_name, request)
        feed = populate_articles_feed(feed, feed_name, request)

    output = feed.writeString('utf-8')

    # output = re.compile('&amp;(\w+);').sub('&\g<1>;', output)
    return HttpResponse(output, content_type=feed.content_type)
