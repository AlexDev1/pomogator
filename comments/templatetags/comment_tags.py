# -*- coding: utf-8 -*-
from itertools import chain
from django import template

from news.models import NewsNewComment

register = template.Library()

@register.inclusion_tag('comments/line_comments.html', takes_context=True)
def line_comments(context, material_id, type):
    comments = 0
    has_more = False
    count = 0

    if type == 'news':
        comments = NewsNewComment.objects.filter(news_entry__id=material_id)
        count = comments.count()
    if type == 'blog':
        comments = BlogEntryComment.objects.filter(blog_entry__id=material_id)
        count = comments.count()
    if type == 'review':
        comments = ReviewComment.objects.filter(review__id=material_id)
        count = comments.count()
    if type == 'photo':
        comments1 = PhotoGalleryComment.objects.filter(gallery__id=material_id)
        comments2 = PictureComment.objects.filter(picture__gallery__id=material_id)
        count = comments1.count() + comments2.count()
        comments = sorted(chain(comments1, comments2), key=lambda obj: obj.datetime)
    if type == 'hotelreview':
        comments = HotelReviewComment.objects.filter(review_entry__id=material_id)
        count = comments.count()
    if type == 'shipreview':
        comments = CruiseShipReviewComment.objects.filter(review_entry__id=material_id)
        count = comments.count()
    if type == 'poireview':
        comments = POIReviewComment.objects.filter(review_entry__id=material_id)
        count = comments.count()

    if comments:
        has_more = False
        if count > 2:
            comments = comments[count-2:]
            has_more = True

    return {'comments': comments, 'has_more': has_more, 'count': count, 'material_id': material_id, 'type': type, 'auth_user': context['auth_user']}
