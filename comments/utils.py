

from obscene_words_filter.regexp import build_bad_phrase
from obscene_words_filter.words_filter import ObsceneWordsFilter
from obscene_words_filter.conf import good_words_re

from .models import ObsceneWord


def get_bad_words():
    from re import compile, IGNORECASE, UNICODE

    words = ObsceneWord.objects.all().values_list('chars', flat=True)

    bad_words = []
    for i in words:
        bad_words.append(build_bad_phrase(i))

    bad_words_re = compile('|'.join(bad_words), IGNORECASE | UNICODE)
    return bad_words_re


def filter_bad_words(s):
    bad_words_re = get_bad_words()

    f = ObsceneWordsFilter(bad_words_re, good_words_re)
    return f.mask_bad_words(s)
