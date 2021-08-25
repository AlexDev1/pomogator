import logging
import os
import re
from datetime import datetime, timedelta
from os.path import join, isdir

from bs4 import BeautifulSoup, Comment
from django.contrib.contenttypes.models import ContentType
from pytils.translit import slugify, translify

from pomogator import settings

log = logging.getLogger(__name__)


def start_date_of_week(date):
    """
    Возвращем дату понедельника текущей недели
    :param date:
    :return: date
    """
    back_to_last_monday = timedelta(days=-date.weekday())
    start_date = datetime.today() + back_to_last_monday
    return start_date


def start_date_of_this_week():
    """
    Возвращем дату -7 дней от текщей
    :return: date
    """
    return start_date_of_week(datetime.today() - timedelta(days=7))


def get_image_path(instance, filename):
    """
    Определяет путь для сохранения картинки в зависимости от модели
    """
    ctype = ContentType.objects.get_for_model(instance)
    model = ctype.model
    dir_name = join(
        'images/upload/',
        str(datetime.now().year),
        str(datetime.now().month),
        str(datetime.now().day)
    )
    return join(dir_name, model, slugify_filename(translify(filename)))


def slugify_filename(name):
    fname = name.rsplit(".", 1)
    fname[0] = slugify(fname[0])
    return ".".join(fname)


# Ресайз картинки (вписывание картинки в заданный прямоугольник)
def resize_image(filename, width=0, height=0):
    WIDTH, HEIGHT = 0, 1
    from PIL import Image
    img = Image.open(filename)

    if width == 0 and height == 0:
        return
    elif width > 0 and height == 0:
        height = img.size[HEIGHT]
    elif width == 0 and height > 0:
        width = img.size[WIDTH]

    if img.size[WIDTH] > width or img.size[HEIGHT] > height:
        img.thumbnail((width, height), Image.ANTIALIAS)
        try:
            img.save(filename, quality=90, optimize=1, dpi=(72, 72))
        except IOError:
            img.save(filename)


# Ресайз картики (точный)
def resize_image_hard(filename, width, height):
    WIDTH, HEIGHT = 0, 1
    from PIL import Image
    img = Image.open(filename)

    log.debug(filename)

    if img.size[WIDTH] > width or img.size[HEIGHT] > height:
        img = img.resize((width, height), Image.ANTIALIAS)
        try:
            img.save(filename, quality=90, optimize=1, dpi=(72, 72))
        except IOError:
            img.save(filename)


# Ресайз картики (точный)
def resize_image_hard_video(filename, file_id, width, height, f_name):
    from PIL import Image
    img = Image.open(filename)
    file, ext = os.path.splitext(filename)

    cur_directory = os.path.join(settings.MEDIA_ROOT, 'images/videopreview/') + str(file_id)

    if not isdir(cur_directory):
        os.mkdir(cur_directory)

    sm_filename = cur_directory + '/' + f_name + ext
    out = img.resize((width, height), Image.ANTIALIAS)
    out.save(sm_filename)


# Очищает текст от определенных HTML-тэгов
def sanitize_html(value, tags=None, attrs=None):
    if tags and len(tags) > 0:
        valid_tags = tags.split()
    else:
        valid_tags = 'p i em strong b u a h1 h2 h3 pre br img ul ol li noindex table tbody tr td span'.split()
    if attrs and len(tags) > 0:
        valid_attrs = attrs.split()
    else:
        valid_attrs = 'href src id class title style rel target border cellspacing cellpadding alt title'.split()
    soup = BeautifulSoup(value)
    for comment in soup.findAll(
        text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        try:
            if tag.name not in valid_tags:
                if tag.name == 'script':
                    tag.extract()
                else:
                    tag.hidden = True
                for attr, val in tag.attrs:
                    if attr in valid_attrs:
                        tag.attrs = (attr, val)
        except Exception as ex:
            print(ex)
        # tag.attrs = [(attr, val) for attr, val in tag.attrs
        #              if attr in valid_attrs]
    # for txt in soup.findAll(True, text=True):  # escaping text to avoid unclosed tags, quotations etc
    #    txt.replaceWith(NavigableString(escape(txt)))
    return soup.renderContents().decode('utf8').replace('javascript:', '')


# Очищает текст от определенных HTML-тэгов
def sanitize_html_with_iframe(value):
    tags = 'p i em strong b u a h1 h2 h3 pre br img ul ol li noindex table tbody tr td span iframe'
    attrs = 'href src id class title style rel target border cellspacing cellpadding alt title width height frameborder allowfullscreen'
    return sanitize_html(value, tags=tags, attrs=attrs)


# Очищает текст от определенных HTML-тэгов
def sanitize_html_no_link(value):
    tags = 'p i em strong b u h1 h2 h3 br img ul ol li table tbody tr td span'
    attrs = 'src id class title style border cellspacing cellpadding alt title'
    return sanitize_html(value, tags=tags, attrs=attrs)


# Очищает текст от определенных HTML-тэгов PANIC VERSION
def sanitize_html_maniac_lite(value):
    tags = 'p a br ul ol li noindex b strong i em table tbody tr td span iframe'
    attrs = 'href class rel border cellspacing cellpadding width height frameborder allowfullscreen'
    return sanitize_html(value, tags=tags, attrs=attrs)


# Очищает текст от определенных HTML-тэгов PANIC VERSION
def sanitize_html_maniac_lite_img(value):
    tags = 'p a br ul ol li noindex b strong i em img table tbody tr td span iframe'
    attrs = 'href rel style src alt id class border cellspacing cellpadding title width height frameborder allowfullscreen'
    return sanitize_html(value, tags=tags, attrs=attrs)


# Очищает текст от определенных HTML-тэгов PANIC VERSION
def sanitize_html_maniac_lite_img_no_link(value):
    tags = 'p br ul ol li noindex b strong i em img span'
    attrs = 'style src alt id class title'
    return sanitize_html(value, tags=tags, attrs=attrs)


# Очищает текст от определенных HTML-тэгов PANIC VERSION
def sanitize_html_maniac(value):
    tags = 'p a br ul ol li noindex span'
    attrs = 'href rel'
    return sanitize_html(value, tags=tags, attrs=attrs)


# Очищает текст от определенных HTML-тэгов PANIC VERSION
def sanitize_html_maniac_no_link(value):
    tags = 'p br ul ol li noindex span'
    attrs = 'name'
    return sanitize_html(value, tags=tags, attrs=attrs)


# Очищает текст от HTML-тэгов COMMENT VERSION - EVERYBODY WANTS TO HACK US
def sanitize_html_comment(value):
    tags = 'p br span'
    attrs = 'name'
    return sanitize_html(value, tags=tags, attrs=attrs)


# Очищает текст от HTML-тэгов COMMENT VERSION - EVERYBODY WANTS TO HACK US
def sanitize_html_tag_desc(value):
    tags = 'br'
    attrs = 'name'
    return sanitize_html(value, tags=tags, attrs=attrs)


# Очищает текст от всех HTML-тэгов
def strip_html(value):
    value = value.replace('&nbsp;', ' ')
    value = value.replace('&laquo;', '"')
    value = value.replace('&raquo;', '"')
    value = value.replace('&ndash;', '"')
    value = value.replace('&middot;', '"')
    soup = BeautifulSoup(value)
    for comment in soup.findAll(
        text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        tag.hidden = True
    return soup.renderContents().decode('utf8').replace('javascript:', '')


# Очищает текст от Word-мусора
def clean_word(txt):
    for i in [
        r'<!--.*?<![^>]*>',
        r'<.--\[if [^>]*>.*?<.\[endif]-->',
        r'<style>.*?</style>',
        r'<(\w:[^>]*?)>.*</\1>',
        r'class=".*?"',
        r'<.--.*?-->',
        r'&lt;!--.*?--&gt;',
        r"""align=["'][^"']*["']""",
        r'{mso-[^}]*}',
    ]:
        r = re.compile(i, re.DOTALL)
        txt = r.sub('', txt)
    return txt


# Определяет путь для сохранения банера в зависимости от рекламодателя
def get_file_path(instance, filename):
    dir_name = 'images/upload/' + ('%s' % datetime.now().year) + '/' + ('%s' % datetime.now().month) + '/' + ('%s' % datetime.now().day)

    dir_name += '/baner/%s' % (instance.user.id)

    try:
        old_name = str(translify(filename)).split('.')
        dt = datetime.now()
        cur_date_str = dt.strftime("%d%m%Y%H%M%S")
        new_name = old_name[0] + '_' + cur_date_str + '.' + old_name[1]
    except:
        new_name = translify(filename)

    # return "%s/%s" %(dir, filename.decode('utf-8').encode('cp1251'))
    # return "%s/%s" %(dir, force_unicode(filename))
    return join(dir_name, new_name)


# Определяет путь для сохранения pdf-каталога
def get_catalog_path(instance, filename):
    path = "files/catalogs/%s/%s" % (instance.user.id, translify(instance.title).replace(",", ""))
    while os.path.exists(path):
        path = '%s_' % path
    return "%s/%s" % (path, translify(filename))

