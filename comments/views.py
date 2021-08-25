# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, Http404
from django.shortcuts import  get_object_or_404

from tourprom.accounts.models import (
    BlogEntry,
    BlogEntryComment,
    CustomUser,
    Review,
    ReviewComment
)
from tourprom.advertisers.models import Advertiser
from tourprom.countries.models import (
    CruiseShipReview,
    CruiseShipReviewComment,
    HotelComment,
    HotelReviewComment,
    POIReview,
    POIReviewComment,
)
from tourprom.custom_utils.refactor import render_to_response
from tourprom.future import JsonResponse
from tourprom.news.models import News, NewsComment
from tourprom.photo.models import (
    PhotoGallery,
    PhotoGalleryComment,
    PictureComment
)

from .models import CommentVote  # Comment

import logging
log = logging.getLogger(__name__)


def ajax_expand_comments(request, type, id):
    if request.is_ajax():
        if type == 'news':
            comments = NewsComment.objects.filter(news_entry__id=id)
        if type == 'blog':
            comments = BlogEntryComment.objects.filter(blog_entry__id=id)
        if type == 'review':
            comments = ReviewComment.objects.filter(review__id=id)
        if type == 'photo':
            comments1 = PhotoGalleryComment.objects.filter(gallery__id=id)
            comments2 = PictureComment.objects.filter(picture__gallery__id=id)
            comments = sorted(
                chain(comments1, comments2), key=lambda obj: obj.datetime)
        if type == 'hotelreview':
            comments = HotelReviewComment.objects.filter(review_entry__id=id)
        if type == 'shipreview':
            comments = CruiseShipReviewComment.objects.filter(
                review_entry__id=id)
        if type == 'poireview':
            comments = POIReviewComment.objects.filter(review_entry__id=id)
        return render_to_response(
            'comments/line_comments_items.html',
            {'comments': comments},
            request=request
        )

    return HttpResponse("Bad request")


def ajax_post_comment(request):
    if request.is_ajax() and request.method == 'POST':
        from django.contrib.auth import get_user
        user = get_user(request)

        text = request.POST["comment-input"]
        id = request.POST["id"]
        c_type = request.POST["type"]
        comment = None
        if c_type == "news":
            if request.user.is_authenticated:
                from django.contrib.auth import get_user
                user = get_user(request)
                if type(user) is CustomUser:
                    user_type = 1
                elif type(user) is Advertiser:
                    user_type = 2
                comment = NewsComment(
                    news_entry=get_object_or_404(News, id=id),
                    user=user,
                    text=text,
                    comment_type=user_type
                )
                comment.save()
        if c_type == "blog":
            if request.user.is_authenticated and type(user) is CustomUser:
                comment = BlogEntryComment(
                    blog_entry=get_object_or_404(BlogEntry, id=id),
                    user=request.user,
                    text=text
                )
                comment.save()
        if c_type == "review":
            if request.user.is_authenticated and type(user) is CustomUser:
                comment = ReviewComment(
                    review=get_object_or_404(Review, id=id),
                    user=request.user,
                    text=text
                )
                comment.save()
        if c_type == "photo":
            if request.user.is_authenticated:
                user = request.user
                comment = PhotoGalleryComment(
                    gallery=get_object_or_404(PhotoGallery, id=id),
                    user=user,
                    text=text
                )
                comment.save()
        if c_type == "hotelreview":
            if request.user.is_authenticated:
                user = request.user
                comment = HotelReviewComment(
                    review_entry=get_object_or_404(HotelComment, id=id),
                    user=user,
                    text=text
                )
                comment.save()
        if c_type == "shipreview":
            if request.user.is_authenticated:
                user = request.user
                comment = CruiseShipReviewComment(
                    review_entry=get_object_or_404(CruiseShipReview, id=id),
                    user=user,
                    text=text
                )
                comment.save()
        if c_type == "poireview":
            if request.user.is_authenticated:
                user = request.user
                comment = POIReviewComment(
                    review_entry=get_object_or_404(POIReview, id=id),
                    user=user,
                    text=text
                )
                comment.save()

        if comment:
            return render_to_response(
                'comments/line_comments_item.html',
                {'comment': comment, 'type': c_type},
                request=request
            )

    return HttpResponse("Bad request")


def ajax_is_auth(request):
    if request.is_ajax():
        if type(request.user) is AnonymousUser:
            ret = "0"
        else:
            ret = "1"
        return HttpResponse(ret)
    return HttpResponse("Bad request")


@login_required
def change_comment_vote_view(request):
    if request.is_ajax():
        log.debug(request.POST)
        cv = CommentVote.objects.filter(
            user=request.user,
            # like=int(request.POST.get('like')),
            object_id=int(request.POST.get('object_id'))
        )
        if cv.exists():
            data = {
                'success': False,
                'status': 'ERROR',
                'message': 'Вы уже голосовали'
            }
            return JsonResponse(data)
        else:
            cv = CommentVote(
                user=request.user,
                like=int(request.POST.get('like')),
                object_id=int(request.POST.get('object_id'))
            )
            cv.save()
            return JsonResponse({'status': 'OK', 'success': True})
    else:
        raise Http404()
