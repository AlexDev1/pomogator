import re

from bs4 import BeautifulSoup

__all__ = ['seo_clean_content']


def seo_clean_content(html):
    html = re.sub('</noindex></noindex>', '', html)
    html = re.sub('<noindex><noindex>', '', html)

    bs = BeautifulSoup(html)

    _url = re.compile('http[s]?:\/\/(www\.)?pomogator\.travel')
    local_host = re.compile('\.\./\.\./\.\./\.\./\.\./')

    for i in bs.findAll("a"):
        if i.has_key('href') and \
                not re.match(_url, i['href']) and \
                not re.match(local_host, i['href']):
            i['rel'] = "nofollow"

    clean_html = bs.renderContents().decode('utf-8')

    return clean_html


def remove_attributes(html, attribute_list=["style", "onclick", "onkeydown"]):
    bs = BeautifulSoup(html)

    for tag in bs():
        for attr in attribute_list:
            del tag[attr]

    return bs.renderContents().decode('utf-8')
